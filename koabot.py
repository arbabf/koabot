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
    def success(self, dice, mods, thresh, comparator, has_equals) -> str:
        # Determines whether a roll succeeded.
        ret_str = ""
        thresh += (2 * int(comparator == '<') - 1) * int(has_equals) + (2 * int(comparator == '>') - 1)
        for i in range(mods[2]):
            roll_str = ""
            arr = self.roll(dice, mods)
            for j in range(len(arr[1])):
                roll_str = "".join([roll_str, ["", ", "][int(j>0)] + str(arr[1][j])])
            has_succeeded = False
            if comparator == '>':
                has_succeeded = arr[0] >= thresh
            else:
                has_succeeded = arr[0] <= thresh
            # This is better than using if statements, trust me. Changes up the return string based on what multiplier number it's on, whether it succeeded, etc.
            ret_str = "".join([ret_str, ("{0}{1}. Threshold was {2}; roll was {3}. [{4}, total modifier {5}].").format(["", "\nRoll {0} has ".format(str(i+1))][int(i>0)], ["failed", "succeeded"][int(has_succeeded)], str(thresh), arr[0], roll_str, str(mods[1]))])
        return ret_str

    def count_successes(self, dice, mods, thresh, comparator, has_equals) -> str:
        # Counts the number of successes.
        ret_str = ""
        thresh += (2 * int(comparator == '<') - 1) * int(has_equals) + (2 * int(comparator == '>') - 1)
        for i in range(mods[2]):
            roll_str = ""
            succ_rolls = 0
            arr = self.roll(dice, mods)
            for elem in arr[1]:
                if comparator == '>':
                    succ_rolls += int(elem + mods[1] >= thresh)
                else:
                    succ_rolls += int(elem + mods[1] <= thresh)
            for j in range(len(arr[1])):
                roll_str = "".join([roll_str, ["", ", "][int(j>0)] + str(arr[1][j])])
            # See success().
            ret_str = "".join([ret_str, ("{0}succeeded {1} time{2}. Threshold was {3}. [{4}, total modifier {5}].").format(["", "\nAttempt {0} ".format(str(i+1))][int(i>0)], str(succ_rolls), ["", "s"][int(succ_rolls!=1)], str(thresh), roll_str, str(mods[1]))])
        return ret_str

    def single_roll(self, dice, mods, thresh, comparator, has_equals) -> str:
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
        # returns: a tuple consisting of count, optional +- and * modifiers, comparator, comparator count, equals sign, 
        # get dice size
        initial_indice = arg_string.find('d')
        indice = initial_indice+1
        if indice == 0:
            return (-1, None, None)
        dice = 0
        while (indice != len(arg_string) and arg_string[indice] in string.digits):
            dice = dice*10 + int(arg_string[indice]) # number concatenation
            indice += 1
        # error messages
        if dice == 0:
            return (-1, None, None)
        comp_count = 0
        comp_index = 0
        last_comp = len(arg_string)
        comp = ''
        has_equals = False
        for char in arg_string:
            # count gt symbols
            if comp == '' and (char == '>' or char == '<'):
                comp = char
                last_comp = comp_index
                comp_count += 1
            elif comp != '' and comp == char:
                last_comp = comp_index
                comp_count += 1
            elif comp != char and comp != '' and char not in string.digits and char != '=':
                return (-1, None, None)
            comp_index += 1
        if last_comp + 1 < len(arg_string) and arg_string[last_comp+1] == '=':
            has_equals = True
            indice = last_comp + 2 # skip the equals
        else:
            indice = last_comp + 1
        thresh = 0
        while indice < len(arg_string) and arg_string[indice] in string.digits:
            # get threshold for gt
            thresh = thresh * 10 + int(arg_string[indice])
            indice += 1
        if indice < len(arg_string) and arg_string[indice] not in string.digits:
            return (-1, None, None)
        if (comp_count >= 3):
            return (-1, None, None)
        count = 1
        indice = initial_indice-1
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
                if indice != len(arg_string) and arg_string[indice] not in string.digits and not (arg_string[indice] in ['+', '-', '*', '>', '<']):
                    # error checking - if we have a non-numeric char or an operand just immediately terminate
                    return (-1, None, None)
                plus_minus_mods.append(num)
                plus_minus_mods[len(plus_minus_mods)-1] += 2 * plus_minus_mods[len(plus_minus_mods)-1] * (int(arg_string[old_index] == '+') - 1) # oneliner to negate number if -, but do nothing if +
            elif arg_string[indice] in ['>', '<']:
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
            if indice != len(arg_string) and arg_string[indice] not in string.digits and not arg_string[indice] in ['>', '<']:
                # error checking
                return(-1, None, None)
            mult_count = num
        return (count, total, mult_count, plus_minus_mods, comp_count, dice, thresh, comp, has_equals)


    @commands.command(name='roll')
    async def roll_start(self, ctx, *args):
        # parses commands given through !roll command
        arg_string = ''
        for arg in args:
            arg_string = "".join([arg_string, arg]) # get the argument string into one contiguous string which we can then parse
        tup = self.parse_args(arg_string)
        if tup[0] == -1:
            await ctx.send("Invalid format. Check !help for a list of allowed formats.")
            return
        if tup[4] == 2 and tup[0] > 1 and len(tup[3]) > 0:
            await ctx.send("Invalid format. Check !help for a list of allowed formats.")
            return
        # switch statement, kinda????
        await ctx.send(ctx.message.author.mention + " has " + [self.single_roll, self.success, self.count_successes][tup[4]](tup[5], tup, tup[6], tup[7], tup[8]))

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
    - !roll d20 - 3 < 8
    - !roll 2d20 >>= 12
    - !roll d20 - 2 + 3 * 5 <<= 15 (* modifier rolls (d20 - 2 + 3) 5 times)
    NOTE: >> or << cannot take more than one die if there exists a +- modifier. Use * to remedy this.
    !flip - flips a coin```""")

bot.add_cog(rollStuff(bot))
bot.run(TOKEN)