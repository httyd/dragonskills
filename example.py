from dragonbot import Skill, command, match

class ExampleSkill(Skill):

    def __init__(self, bot):

        self.bot = bot

        self.dragon_count = 0
        self.last_dragon = None


    @command("name")
    def name(self, message, args):

        message.reply("Your name is " + message.nick + ".")


    @command("admin", admin = True)
    def admin(self, message, args):

        message.reply("/me bows down to " + message.nick + ".")


    @match("dragon(?! stats)")
    def dragons(self, message):

        self.dragon_count += 1
        self.last_dragon = message


    @command("dragon stats")
    def dragon_stats(self, message, args):

        message.reply("Dragon count: " + str(self.dragon_count) + "\n" +
                      "Last dragon: " + repr(self.last_dragon))
