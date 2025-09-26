/**
 * The Telegram Connector is a scheduled Cloudflare Worker that fetches messages from Telegram channels and stores them
 *
 * ## Functional Requirements
 *
 * - Access Telegram using `env.TELETHON` containerized version of `telethon` library.
 * - Authorize using sessions stored in `SESSION` KV, in following format:
 * ```js
 * "accountSession":{
 *  "api_id": "123",
 *  "api_hash": "dsfadsfasdfa",
 *  "session_str": "r42fd23f2f"}
 * ```
 * - Fetch messages all new messages and store in `MESSAGES` KV.
 *
 * ### `MESSAGES` KV entry example
 * ```js
 * messageId: { content, timestamp, userName, userId, messageId, channelName }
 * ```
 * ## Additional Documentation
 *
 * ### Containers in Cloudflare Worker
 * ```js
 * import { Container, getContainer } from "@cloudflare/containers";
 *
 * export class MyContainer extends Container {
 *   defaultPort = 4000; // Port the container is listening on
 *   sleepAfter = "10m"; // Stop the instance if requests not sent for 10 minutes
 * }
 *
 * export default {
 *   async fetch(request, env) {
 *     const { "session-id": sessionId } = await request.json();
 *     // Get the container instance for the given session ID
 *     const containerInstance = getContainer(env.MY_CONTAINER, sessionId);
 *     // Pass the request to the container instance on its default port
 *     return containerInstance.fetch(request);
 *   },
 * };
 * ```
 */

import { Container, getContainer } from "@cloudflare/containers"

export class MyContainer extends Container {
  defaultPort = 8080
  sleepAfter = "10s"

  envVars = {
    TELEGRAM_API_ID: env.TELEGRAM_API_ID,
    TELEGRAM_API_HASH: env.TELEGRAM_API_HASH,
    TELEGRAM_SESSION_STR: env.TELEGRAM_SESSION_STR,
  }
}

export default {
  async scheduled(request, env) {
    const containerInstance = getContainer(env.CONTAINER, "theOnlyOne")
    return containerInstance.fetch("")
  },
}
