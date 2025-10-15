This service runs on Cloudflare Workers with containers. It periodically retrieves new messages from Telegram and stores them in a Timescale database. Consecutive messages from the same author within the same channel are merged into a single message by concatenating their text and retaining the metadata of the last message.

## Timescale Setup
[Create](https://console.cloud.timescale.com/signup) a Timescale database with their 30 days free trial. You will need to add connection string to `TIMESCALE_CONNECTION` secret.

Use queries below to set up schema.

```sql
CREATE TABLE IF NOT EXISTS "message_feed" (
	"id" integer GENERATED ALWAYS AS IDENTITY (sequence name "message_feed_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"timestamp" timestamp with time zone DEFAULT now() NOT NULL,
	"platform_name" text NOT NULL,
	"platform_user_id" text NOT NULL,
	"platform_user_name" text NOT NULL,
	"platform_message_id" text NOT NULL,
	"platform_message_url" text,
	"source_account_id" text NOT NULL,
	"source_channel_name" text,
	"source_channel_id" text,
	"platform_specific" jsonb,
	"message_id" integer NOT NULL,
	CONSTRAINT "message_feed_id_timestamp_pk" PRIMARY KEY("id","timestamp"),
	CONSTRAINT "message_feed_timestamp_platform_name_platform_message_id_unique" UNIQUE("timestamp","platform_name","platform_message_id")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "unique_messages" (
	"id" integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY (sequence name "unique_messages_id_seq" INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START WITH 1 CACHE 1),
	"content" text NOT NULL,
	"embedding" text DEFAULT null,
	CONSTRAINT "unique_messages_content_unique" UNIQUE("content")
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "message_feed" ADD CONSTRAINT "message_feed_message_id_unique_messages_id_fk" FOREIGN KEY ("message_id") REFERENCES "public"."unique_messages"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
```

## Obtaining Telegram Credentials for testing

Use dedicated account for testing. Follow [this guide](https://docs.telethon.dev/en/stable/basic/signing-in.html#signing-in) to register a Telegram application and save your `api_id` and `api_hash`.

Then generate session string using [container/scripts/generate_session_str.py](container/scripts/generate_session_str.py). Prior to executing the script, make sure to install [telethon](https://docs.telethon.dev/en/stable/basic/installation.html#installation).

The script will request input for the `api_id` and `api_hash`. Additionally, it will ask for the phone number associated with the account, and a verification code will be sent to that number. You will find session string printed out in your terminal. 

Then you can add these three as Cloudflare Secrets: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` and `TELEGRAM_SESSION_STR`.

## Useful Resources

- [Deploying Cloudflare Worker with container](https://developers.cloudflare.com/containers/get-started/)
- [Telethon Documentation](https://docs.telethon.dev/en/stable/)