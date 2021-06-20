# The Kingdoms of Atlantica bot.
# Author: arbabf

import os
import string
import random
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

keep_alive()
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
bot.remove_command("help")


class rollStuff(commands.Cog):
    def success(self, dice, mods, thresh) -> str:
        # Determines whether a roll succeeded.
        ret_str = ""
        for i in range(mods[2]):
            roll_str = ""
            arr = self.roll(dice, mods)
            for j in range(len(arr[1])):
                roll_str = "".join([roll_str, ["", ", "][int(j>0)] + str(arr[1][j])])
            # This is better than using if statements, trust me. Changes up the return string based on what multiplier number it's on, whether it succeeded, etc.
            ret_str = "".join([ret_str, ("{0}{1}. Threshold was {2}; roll was {3}. [{4}, total modifier {5}].").format(["", "\nRoll {0} has ".format(str(i+1))][int(i>0)], ["failed", "succeeded"][int(arr[0] > thresh)], str(thresh), arr[0], roll_str, str(mods[1]))])
        return ret_str

    def count_successes(self, dice, mods, thresh) -> str:
        # Counts the number of successes.
        ret_str = ""
        for i in range(mods[2]):
            roll_str = ""
            succ_rolls = 0
            arr = self.roll(dice, mods)
            for elem in arr[1]:
                if elem + mods[1] > thresh:
                    succ_rolls += 1
            for j in range(len(arr[1])):
                roll_str = "".join([roll_str, ["", ", "][int(j>0)] + str(arr[1][j])])
            # See success().
            ret_str = "".join([ret_str, ("{0}succeeded {1} time{2}. Threshold was {3}. [{4}, total modifier {5}].").format(["", "\nAttempt {0} ".format(str(i+1))][int(i>0)], str(succ_rolls), ["", "s"][int(succ_rolls!=1)], str(thresh), roll_str, str(mods[1]))])
        return ret_str

    def single_roll(self, dice, mods, thresh) -> str:
        # Singular roll.
        ret_str = ""
        for i in range(mods[2]):
            roll_str = ""
            arr = self.roll(dice, mods)
            for j in range(len(arr[1])):
                roll_str = "".join([roll_str, ["", ", "][int(j>0)] + str(arr[1][j])])
            #See success().
            ret_str = "".join([ret_str, "{0}rolled {1}. [{2}, total modifier {3}]."]).format(["", "\nAlso "][int(i>0)],arr[0], roll_str, str(mods[1]))
        return ret_str
    
    def roll(self, dice, mods) -> list:
        # chucks a roll w/ modifiers if there are any
        sum = 0
        roll_results = []
        for _ in range(mods[0]):
            num = random.randint(1, dice)
            roll_results.append(num)
            sum += num
        sum += mods[1]
        return [sum, roll_results]

    def parse_args(self, arg_string):
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
        while indice != len(arg_string) and arg_string[indice] in string.digits:
            indice += 1 #stupid workaround, fix later
        while indice != len(arg_string) and arg_string[indice] != '*':
            # look for every +/- modifier
            if arg_string[indice] in ['+', '-']:
                num = 0
                indice += 1
                old_index = indice-1
                while indice != len(arg_string) and arg_string[indice] in string.digits:
                    num = num * 10 + int(arg_string[indice])
                    indice += 1
                if indice != len(arg_string) and arg_string[indice] not in string.digits and not (arg_string[indice] in ['+', '-', '*', '>']):
                    # error checking - if we have a non-numeric char or an operand just immediately terminate
                    return (-1, None, None)
                plus_minus_mods.append(num)
                plus_minus_mods[len(plus_minus_mods)-1] += 2 * plus_minus_mods[len(plus_minus_mods)-1] * (int(arg_string[old_index] == '+') - 1) # oneliner to negate number if -, but do nothing if +
            elif arg_string[indice] == '>':
                break
            else:
                return (-1, None, None)
        total = 0
        mult_count = 1
        for elem in plus_minus_mods:
            total += elem
        if indice != len(arg_string) and arg_string[indice] == '*':
            # look for how many times we should repeat this roll
            indice += 1
            num = 0
            while indice != len(arg_string) and arg_string[indice] in string.digits:
                num = num * 10 + int(arg_string[indice])
                indice += 1
            if indice != len(arg_string) and arg_string[indice] not in string.digits and not arg_string[indice] == '>':
                # error checking
                return(-1, None, None)
            mult_count = num
        return (count, total, mult_count, plus_minus_mods)


    @commands.command(name='roll')
    async def roll_parse(self, ctx, *args):
        # parses commands given through !roll command
        # only parses dice, gt
        arg_string = ''
        for arg in args:
            arg_string += arg # get the argument string into one contiguous string which we can then parse
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
        gt_count = 0
        gt_index = 0
        last_gt = len(arg_string)
        for char in arg_string:
            # count gt symbols
            if char == '>':
                last_gt = gt_index
                gt_count += 1
            gt_index += 1
        indice = last_gt + 1
        thresh = 0
        while indice < len(arg_string) and arg_string[indice] in string.digits:
            # get threshold for gt
            thresh = thresh * 10 + int(arg_string[indice])
            indice += 1
        if indice < len(arg_string) and arg_string[indice] not in string.digits:
            await ctx.send("Invalid format. Check !help for a list of allowed formats.")
            return
        if (gt_count >= 3):
            await ctx.send("Invalid format. Check !help for a list of allowed formats.")
            return
        tup = self.parse_args(arg_string)
        if tup[0] == -1:
            await ctx.send("Invalid format. Check !help for a list of allowed formats.")
            return
        if gt_count == 2 and tup[0] > 1 and len(tup[3]) > 0:
            await ctx.send("Invalid format. Check !help for a list of allowed formats.")
            return
        # switch statement, kinda????
        await ctx.send(ctx.message.author.mention + " has " + [self.single_roll, self.success, self.count_successes][gt_count](dice, tup, thresh))

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
Commands:
    !help - brings up this help text
    !roll - rolls dice. Parameters:
    <optional number of dice> d <number of faces> <optional +- modifiers> <optional repetition modifier>
    Optional: Use > to sum up each individual dice roll, or >> to count successes.
    Example rolls:
    - !roll d20
    - !roll 3d6
    - !roll d20 + 5 > 12
    - !roll 2d20 >> 12
    - !roll d20 - 2 + 3 * 5 >> 15 (* modifier rolls (d20 - 2 + 3) 5 times)
    NOTE: >> cannot take more than one die. Use * to remedy this.
    !flip - flips a coin
    !pref - change command prefix```""")

@bot.command(name='pref')
async def pref(ctx):
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send("Type in the prefix you would like (max 10 characters):")
        def check(msg):
            if len(msg.content) <= 10 and msg.author == ctx.message.author:
                return msg
        try:
            new_pref = await bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send("Taken too long to set a prefix!")
        else:
            await ctx.send("New prefix set to {0}.".format(new_pref.content))
            bot.command_prefix = new_pref.content
    else:
        await ctx.send("Only a user with administrator permissions can perform this command.")
bot.add_cog(rollStuff(bot))
bot.run(TOKEN)