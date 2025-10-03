/**
 * The Telegram Connector is a scheduled Cloudflare Worker that fetches messages from Telegram channels and stores them
 *
 * ## Functional Requirements
 *
 * - Access Telegram using `env.CONTAINER`.
 * - Fetch messages all new messages and log them out.
 * - Save last fetched message ID per `sourceChannelId` in `POINTERS` KV, in following format: `"%sourceChannelId%": "%lastMessageId%"`
 * - Skip `lastMessageIds` if KV is empty (first run).
 *
 * ### Output entry example
 * ```js
 * messageId: { content, timestamp, userName, userId, messageId, channelName, sourceChannelId }
 * ```
 * 
 * ## Best Practices
 * - Simplicity, reliability, and efficiency.
 * - Stick to JSDoc for specifications, documentation, and type definitions.
 * - Robust error handling and logging techniques with succinct messages. Wrapping each data processing stage in a try-catch block, validating all inputs and outputs, and using `INFO` and `ERROR` levels with detailed contextual information, such as processing stage, task name, etc.
 * - Concise code with minimal formatting and indentation, which prioritizes descriptive element naming and log messages over inline comments to achieve readability.
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
import { env } from "cloudflare:workers"

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
  async scheduled(ctx, env) {
    try {
      // Fetch last message IDs from POINTERS KV
      const pointersList = await env.POINTERS.list()
      console.log("Fetched pointersList:", pointersList)
      const lastMessageIds = pointersList.keys.map((key) => key.name)
      console.log("Last message IDs:", lastMessageIds)
      const url = "https://example.com/?" + new URLSearchParams({ lastMessageIds: lastMessageIds.join(",") })
      console.log("Request URL:", url)

      const containerInstance = getContainer(env.CONTAINER, "theOnlyOne")
      console.log("Container instance created")

      const messages = await containerInstance.fetch(url)
      const messagesJson = await messages.json()
      console.log("Fetched messages:", messagesJson)

      // Store biggest message IDs for each source back to POINTERS KV
      const newPointers = {}
      messagesJson.forEach((message) => {
        const currentMax = newPointers[message.sourceChannelId] || "0"
        if (message.platformMessageId > currentMax) {
          newPointers[message.sourceChannelId] = message.platformMessageId
        }
      })
      console.log("New pointers to store:", newPointers)
      await Promise.all(
        Object.entries(newPointers).map(([sourceChannelId, lastMessageId]) =>
          env.POINTERS.put(sourceChannelId, lastMessageId)
        )
      )
      console.log("Pointers stored successfully")
      return new Response("Success", { status: 200 })
      
    } catch (e) {
      console.error("Error in scheduled handler:", e)
      return new Response(e.message, { status: 500 })
    }
  },
}
