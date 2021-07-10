# koabot
DnD bot for our homebrewed campaign. Made to be an improvement over RPBot, tuned to our specific needs.

Requires the ability to read and send messages. Use the link below to add the bot to your server.<br>
https://discord.com/api/oauth2/authorize?client_id=818385880758747156&permissions=76800&scope=bot

Commands:  
    !help - brings up this help text  
    !roll - rolls dice.  
	Parameters: [optional number of dice] d [number of faces] [optional +- modifiers] [optional repetition modifier]  
    Optional: Use > to sum up each individual dice roll, or >> to count successes.  
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
    !flip - flips a coin  
