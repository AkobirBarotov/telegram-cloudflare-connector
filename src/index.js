import { Container, getContainer } from "@cloudflare/containers";
import { env } from "cloudflare:workers";

export class MyContainer extends Container {
  // Container port (Flask listens on this port)
  defaultPort = 8080;

  // IMPORTANT CHANGE: 
  // Extend time from 10s to 10m to prevent container termination.
  // This allows synchronization of large volumes of messages.
  sleepAfter = "10m";

  envVars = {
    TELEGRAM_API_ID: env.TELEGRAM_API_ID,
    TELEGRAM_API_HASH: env.TELEGRAM_API_HASH,
    TELEGRAM_SESSION_STR: env.TELEGRAM_SESSION_STR,
    TIMESCALE_CONNECTION: env.TIMESCALE_CONNECTION,
  };
}

export default {
  async scheduled(ctx, env) {
    try {
      console.log("[Worker] Scheduled event started. Waking up container...");

      const url = "http://localhost:8080/";
      // Determine container name (use default if env.CONTAINER is missing)
      const containerInstance = getContainer(env.CONTAINER || "telegram-connector-container", "telegram-worker-1");

      // Send request to container - this "wakes it up" and runs main.py
      const resp = await containerInstance.fetch(url);

      if (!resp.ok) {
        const errText = await resp.text();
        console.error(`[Worker] Container Error: ${resp.status} - ${errText}`);
        throw new Error(`Container returned status ${resp.status}`);
      }

      const data = await resp.json();
      console.log("[Worker] Sync Success:", JSON.stringify(data));

      return new Response("Sync Completed Successfully", { status: 200 });

    } catch (e) {
      console.error("[Worker] Critical Error in scheduled handler:", e);
      // Return 200 even on error to prevent Cloudflare from retrying (spamming),
      // but the error will be visible in the logs.
      return new Response(`Error: ${e.message}`, { status: 500 });
    }
  },
};
