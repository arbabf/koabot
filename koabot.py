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
    def success(self, dice, mods, thresh, comparator, has_equals, low_roll_type, low_roll_count) -> str:
        # Determines whether a roll succeeded.
        ret_str = ""
        thresh += (2 * int(comparator == '<') - 1) * int(has_equals) + (2 * int(comparator == '>') - 1)
        for i in range(mods[2]):
            roll_str = ""
            arr = self.roll(dice, mods, low_roll_type, low_roll_count)
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

    def count_successes(self, dice, mods, thresh, comparator, has_equals, low_roll_type, low_roll_count) -> str:
        # Counts the number of successes.
        ret_str = ""
        thresh += (2 * int(comparator == '<') - 1) * int(has_equals) + (2 * int(comparator == '>') - 1)
        for i in range(mods[2]):
            roll_str = ""
            succ_rolls = 0
            arr = self.roll(dice, mods, low_roll_type, low_roll_count)
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

    def single_roll(self, dice, mods, thresh, comparator, has_equals, low_roll_type, low_roll_count) -> str:
        # Singular roll. 
        # thresh, comparator, has_equals do nothing by design - this is to keep the 'switch' statement seen in roll_start.
        ret_str = ""
        for i in range(mods[2]):
            roll_str = ""
            arr = self.roll(dice, mods, low_roll_type, low_roll_count)
            for j in range(len(arr[1])):
                roll_str = "".join([roll_str, ["", ", "][int(j>0)] + str(arr[1][j])])
            #See success().
            ret_str = "".join([ret_str, "{0}rolled {1}. [{2}, total modifier {3}]."]).format(["", "\nAlso "][int(i>0)],arr[0], roll_str, str(mods[1]))
        return ret_str
    
    def roll(self, dice, mods, low_roll_type, low_roll_count) -> list:
        # chucks a roll w/ modifiers if there are any
        sum = 0
        roll_results = []
        for _ in range(mods[0]):
            num = random.randint(1, dice)
            roll_results.append(num)
            sum += num
        roll_results = sorted(roll_results)
        if low_roll_type != 0:
            for i in range(low_roll_count):
                sum -= roll_results[i]
                if low_roll_type == 1:
                    num = random.randint(1, dice)
                    roll_results[i] = num
                    sum += num
            if low_roll_type == 2:
                roll_results = roll_results[low_roll_count:]
        sum += mods[1]
        random.shuffle(roll_results) # because I don't like how it comes out all in order - even this is better.
        return [sum, roll_results]

    def parse_args(self, arg_string):
        # does the actual parsing
        # returns: a tuple consisting of count, optional +- and * modifiers, comparator, comparator count, equals sign, what to do with low rolls, and the number of low rolls we should affect
        failure = (-1, None, None)
        concat_num = lambda x : x * 10 + int(arg_string[indice]) # number concatenation, using arg_string[indice] so I don't have to write it 50 times

        initial_indice = arg_string.find('d')
        indice = initial_indice+1
        
        # get dice size
        if indice == 0:
            return failure
        dice = 0
        while (indice != len(arg_string) and arg_string[indice] in string.digits):
            dice = concat_num(dice) 
            indice += 1
        # error messages
        if dice == 0:
            return failure
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
            return failure
        indice = initial_indice+1
        while indice != len(arg_string) and arg_string[indice] in string.digits:
            indice += 1 #stupid workaround, fix later
        while indice != len(arg_string) and arg_string[indice] != '*':
            # look for every +/- modifier
            if arg_string[indice] in ['+', '-']:
                num = 0
                indice += 1
                old_index = indice-1
                while indice != len(arg_string) and arg_string[indice] in string.digits:
                    num = concat_num(num)
                    indice += 1
                if indice != len(arg_string) and arg_string[indice] not in string.digits and not (arg_string[indice] in ['+', '-', '*', '>', '<', 'r', 'f']):
                    # error checking - if we have a non-numeric char or an operand just immediately terminate
                    return failure
                plus_minus_mods.append(num)
                plus_minus_mods[len(plus_minus_mods)-1] += 2 * plus_minus_mods[len(plus_minus_mods)-1] * (int(arg_string[old_index] == '+') - 1) # oneliner to negate number if -, but do nothing if +
            elif arg_string[indice] in ['>', '<', 'r', 'f']:
                break
            else:
                return failure
        total = 0
        mult_count = 1
        for elem in plus_minus_mods:
            total += elem
        if indice != len(arg_string) and arg_string[indice] == '*':
            # look for how many times we should repeat this roll
            indice += 1
            num = 0
            while indice != len(arg_string) and arg_string[indice] in string.digits:
                num = concat_num(num)
                indice += 1
            if indice != len(arg_string) and arg_string[indice] not in string.digits and not arg_string[indice] in ['>', '<', 'r', 'f']:
                # error checking
                return failure
            mult_count = num
        low_roll_type = 0 # 0 for don't do anything to the lowest roll(s), 1 for reroll lowest roll(s), 2 for drop lowest roll(s).
        low_roll_count = 0
        if indice < len(arg_string):
            if arg_string[indice] == 'r':
                low_roll_type = 1
                indice += 1
            elif arg_string[indice] == 'f':
                low_roll_type = 2
                indice += 1
        while indice < len(arg_string) and arg_string[indice] in string.digits:
            low_roll_count = concat_num(low_roll_count)
            indice += 1
        if low_roll_type != 0 and low_roll_count == 0:
            # Default case if we specify what to do with the lowest roll(s). Happens in cases where our command is something like !roll 3d20r>10.
            low_roll_count = 1
        if low_roll_count >= count:
            return failure
        comp_count = 0
        last_comp = len(arg_string)
        comp = ''
        has_equals = False
        while indice < len(arg_string) and arg_string[indice] in ['>', '<']:
            char = arg_string[indice]
            # count gt symbols
            if comp == '' and (char == '>' or char == '<'):
                comp = char
                last_comp = indice
                comp_count += 1
            elif comp != '' and comp == char:
                last_comp = indice
                comp_count += 1
            elif comp != char and comp != '' and char not in string.digits and char != '=':
                return failure
            indice += 1
        if last_comp + 1 < len(arg_string) and arg_string[last_comp+1] == '=':
            has_equals = True
            indice = last_comp + 2 # skip the equals
        else:
            indice = last_comp + 1
        thresh = 0
        while indice < len(arg_string) and arg_string[indice] in string.digits:
            # get threshold for gt
            thresh = concat_num(thresh)
            indice += 1
        if indice < len(arg_string) and arg_string[indice] not in string.digits:
            return failure
        if (comp_count >= 3):
            return failure
        return (count, total, mult_count, plus_minus_mods, comp_count, dice, thresh, comp, has_equals, low_roll_type, low_roll_count)


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
        await ctx.send(ctx.message.author.mention + " has " + [self.single_roll, self.success, self.count_successes][tup[4]](tup[5], tup, tup[6], tup[7], tup[8], tup[9], tup[10]))

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
    Optional: Use > and < to sum up each individual dice roll, or >> and << to count successes use r and f to reroll or drop the lowest rolls - you can specify how many rolls to reroll/drop. Default is one.
    Example rolls:
    - !roll d20
    - !roll 3d6
    - !roll d20 + 5 > 12
    - !roll d20 - 3 < 8
    - !roll 2d20 >>= 12
    - !roll d20 - 2 + 3 * 5 <<= 15 (* modifier rolls (d20 - 2 + 3) 5 times)
    - !roll 3d20 + 3f (rolls 3d20+3, drops the lowest roll)
    - !roll 5d20 + 3 * 2r3 (rolls 5d20 + 3 twice, and rerolls the three lowest rolls of each)
    NOTE: >> and << cannot take more than one die if there exists a +- modifier. Use * to remedy this.
    !flip - flips a coin```""")

bot.add_cog(rollStuff(bot))
bot.run(TOKEN)