# The Kingdoms of Atlantica bot.

import os
import discord
import string
import random
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
bot.remove_command("help")


class rollStuff(commands.Cog):
    def success(self, arg_string, mods):
        pass

    def count_successes(self, arg_string, mods):
        pass

    def roll(self, dice, mods):
        # chucks a roll w/ modifiers if there are any
        sum = 0
        roll_results = []
        for _ in range(mods[0]):
            num = random.randint(1, dice)
            roll_results.append(num)
            sum += num

    def parse_args(self, arg_string, ctx):
        # does the actual parsing
        # returns: a tuple consisting of count and optional +- and * modifiers
        count = 1
        indice = arg_string.find('d')-1
        count_string = ''
        plus_minus_mods = []
        while (indice >= 0):
            # backwards number concatenation using strings
            count_char = arg_string[indice]
            count_char += count_string
            count_string = count_char
            indice -= 1
        try:
            # catch bad counts
            if (count_string == ''):
                pass
            elif(int(count_string) <= 0):
                raise Exception
            else:
                count = int(count_string)
        except Exception:
            return (-1, None, None)
        indice = arg_string.find('d')+1
        while indice != len(arg_string) and arg_string[indice] != '*':
            pass
        return (count, None, None)


    @commands.command(name='roll')
    async def roll_parse(self, ctx, *args):
        # parses commands given through !roll command
        arg_string = ''
        for arg in args:
            arg_string += arg # get the argument string into one contiguous string which we can then parse
        gt_count = 0
        for char in arg_string:
            # count gt symbols
            if char == '>':
                gt_count += 1
        # get dice size
        indice = arg_string.find('d')+1
        if indice == 0:
            await ctx.send("Incorrect format! Check !help for a list of allowed formats.")
            return
        dice = 0
        while (indice != len(arg_string) and arg_string[indice] in string.digits):
            dice = dice*10 + int(arg_string[indice]) # number concatenation
            indice += 1
        # error messages
        if dice == 0:
            await ctx.send("Number of faces must be greater than 0!")
            return
        if (gt_count >= 3):
            await ctx.send("Invalid format.")
            return

        tup = self.parse_args(arg_string, ctx)
        if tup[0] == -1:
            await ctx.send("Invalid format. Check !help for a list of allowed formats.")
            return
        await ctx.send([
            # switch statement, sort of (this has no right to exist)
            self.roll(dice, tup),
            self.success(dice, tup),
            self.count_successes(dice, tup)
        ][gt_count])

@bot.command(name='flip')
async def flip(ctx):
    # flips a virtual coin
    if (random.randint(1, 2) == 1):
        await ctx.send("Tails!")
    else:
        await ctx.send("Heads!")

@bot.command(name='help')
async def help(ctx):
    await ctx.send("""```Kingdoms of Atlantica bot. Made to be an improvement over RPBot, tuned to our specific group's needs.\n
    Commands:\n
    !help - brings up this help text\n
    !roll - rolls dice. Parameters:\n
    <optional number of dice> d <number of faces> <optional +- modifiers> <optional repetition modifier>\n
    Optional: Use > to sum up each individual dice roll, or >> to count successes.\n
    Example rolls:\n
    - !roll d20\n
    - !roll 3d6\n
    - !roll d20 > 12\n
    - !roll 2d20 + 2 >> 12\n
    - !roll 3d20 - 2 + 3 * 5 >> 15 (* modifier rolls (3d20 - 2 + 3) 5 times)\n
    !flip - flips a coin\n
    !pref - change command prefix```""")

@bot.command(name='pref')
async def pref(ctx):
    await ctx.send("Type in the prefix you would like (max 10 characters):")
    def check(msg):
        if len(msg.content) <= 10:
            return msg
    try:
        new_pref = await bot.wait_for("message", check=check, timeout=60.0)
    except asyncio.TimeoutError:
        await ctx.send("Taken too long to set a prefix!")
    else:
        await ctx.send("New prefix set to {0}.".format(new_pref.content))
        bot.command_prefix = new_pref.content

bot.add_cog(rollStuff(bot))
bot.run(TOKEN)