import random
import re

from dragonbot import Skill, command, match

class Rule:

    def __init__(self, bot, creator, text):

        self.creator = creator
        self.text = text
        self.botName = bot.name()
        self.lengthRange = (3, 100)

        self.parse()


    def parse(self):

        matches = re.match("^\s*(?:(.*?)\s*&)?\s*(.*)\s*->\s*(.*?)\s*$", self.text)

        if not matches:
            raise ValueError("Invalid rule.")

        groups = matches.groups()

        if groups[0]:
            self.triggers = [s.strip() for s in groups[0].split("|")]
        else:
            self.triggers = None

        self.antecedents = [s.strip() for s in groups[1].split("|")]
        self.consequents = [s.strip() for s in groups[2].split("|")]

        minAntecedent = min([len(s) for s in self.antecedents])
        maxConsequent = max([len(s) for s in self.consequents])

        if minAntecedent < self.lengthRange[0] or maxConsequent > self.lengthRange[1]:
            raise ValueError("Invalid rule.")

        return True


    def substitute(self, caller, string):

        return string.replace("$me", self.creator) \
                     .replace("$my", self.creator + "'s") \
                     .replace("$your", caller + "'s") \
                     .replace("$you", caller) \
                     .replace("$they", caller) \
                     .replace("$them", caller) \
                     .replace("$she", caller) \
                     .replace("$her", caller) \
                     .replace("$he", caller) \
                     .replace("$their", caller + "'s") \
                     .replace("$his", caller + "'s") \
                     .replace("$hers", caller + "'s") \
                     .replace("$digit", str(random.randint(0,9))) \
                     .replace("$nonzero", str(random.randint(1,9))) \
                     .replace("$bot", self.botName)


    def generate(self, message, antecedent, consequent):

        pattern = "\\b" + re.escape(self.substitute(message.nick, antecedent)) \
                    .replace(re.escape("**"), "(.*)") \
                    .replace(re.escape("*"), "(?:\\b(\\w+)|(\\w+)\\b|(\\w+))") \
                    .replace(re.escape("^^"), ".*") \
                    .replace(re.escape("^"), "\\w*") + "\\b"

        matches = re.match(".*"+pattern+".*", message.body, re.IGNORECASE)

        if not matches:

            return None

        groups = [group for group in matches.groups() if group]
        action = self.substitute(message.nick, consequent)

        for index, group in enumerate(groups):

            if len(group) > 0 and group[-1] in [",", ".", "?", "!", ":", ";", "/"]:
                group = group[:-1]

            action = action.replace("$" + str(index+1), group)

        return action


    def run(self, message):

        triggered = True

        if self.triggers:

            triggered = False

            for trigger in self.triggers:
                if self.substitute(message.nick, trigger).lower() in message.body.lower():

                    triggered = True
                    break

        if triggered:
            for antecedent in self.antecedents:

                result = self.generate(message,
                                    antecedent,
                                    random.choice(self.consequents))

                if result: 
                    return result

        return None


    def __str__(self):

        result = self.creator + ": "

        if self.triggers:
            result += " | ".join(self.triggers) + " & "

        result += " | ".join(self.antecedents) + " -> "
        result += " | ".join(self.consequents)

        return result
    

    def __repr__(self):

        return self.__str__()


class Training(Skill):

    def __init__(self, bot):

        self.bot = bot
        self.rules = []
        self.last = None
        self.sleeping = False


    @match("^@Toothless.*->")
    def train(self, message):

        if self.sleeping:
            return

        body = message.body[len("@" + self.bot.name()):]

        try:

            self.rules.append(Rule(self.bot, message.nick, body))
            message.reply("/me was trained by " + message.nick + ".")

        except:

            message.reply("/me didn't understand.")


    @match("")
    def match(self, message):

        if "->" in message.body or self.sleeping:
            return

        choices = [(rule, rule.run(message))
                for rule
                in self.rules
                if rule.run(message)]

        if len(choices) > 0:

            choice = random.choice(choices)
            message.reply(choice[1])
            self.last = choice[0]


    @command("last")
    def lastrule(self, message, args):

        if self.last:

            message.reply("/me last used: " + str(self.last))

        else:

            message.reply("/me can't remember the last rule.")


    @command("forget")
    def forgetlast(self, message, args):

        try:

            number = int(args[0])
            forgot = self.rules.pop(number-1)
            message.reply("/me forgot: " + str(forgot))

            if self.last == forgot:
                self.last = None

        except:

            if self.last:

                message.reply("/me forgot: " + str(self.last))
                self.rules.remove(self.last)
                self.last = None

            else:

                message.reply("/me can't remember what to forget.")


    @command("everything")
    def everything(self, message, args):

        everything = "\n".join([str(r+1) + ". " + str(rule).replace("://","[:]//") for r, rule in enumerate(self.rules)])
        message.reply("All trained rules:\n\n" + everything)


    @command("sleep", admin = True)
    def sleep(self, message, args):

        self.sleeping = True
        message.reply("/me fell asleep.")


    @command("wake", admin = True)
    def wake(self, message, args):

        self.sleeping = False
        message.reply("/me woke up!")
