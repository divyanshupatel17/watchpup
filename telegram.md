# Step 1 – Create a bot (one-time)
 - Open Telegram and search for `@BotFather`
 - Then press **Start** and send `/newbot`
 - BotFather will ask for:
   * bot name
   * bot username
   fill these appropriately
 - You’ll finally receive something like `1234567890:AAFx...your_bot_token`

# Step 2 – Get your chat_id
 - Open your new bot in Telegram and press **Start**.
 - Send any message to initialise the bot like `hi`.
 - After initialising, open the following URL in your browser:
```
https://api.telegram.org/bot<BOT_TOKEN>/getUpdates
```
(Replace `<BOT_TOKEN>` with your real token)
 - You will see a JSON response like:
```json
{
  "message": {
    "chat": {
      "id": 123456789
    }
  }
}
```
 - That number is your `chat id`

# Step 3 – Store them in your `.env`

```env
TG_BOT_TOKEN=1234567890:AAFx....
TG_CHAT_ID=123456789
```