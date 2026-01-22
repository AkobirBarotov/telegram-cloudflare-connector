import { Container, getContainer } from "@cloudflare/containers";
import { env } from "cloudflare:workers";

export class MyContainer extends Container {
  // Konteyner porti (Flask shu portda eshitadi)
  defaultPort = 8080;
  
  // MUHIM O'ZGARISH: 
  // Konteyner o'chib qolmasligi uchun vaqtni 10 soniyadan 10 daqiqaga cho'zamiz.
  // Bu katta hajmdagi xabarlarni sinxronizatsiya qilishga imkon beradi.
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
      // Konteyner nomini aniqlaymiz (agar env.CONTAINER bo'lmasa, default nom ishlatamiz)
      const containerInstance = getContainer(env.CONTAINER || "telegram-connector-container", "telegram-worker-1");

      // Konteynerga so'rov yuborish - bu uni "uyg'otadi" va main.py ni ishga tushiradi
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
      // Xatolik bo'lsa ham 200 qaytaramizki, Cloudflare qayta-qayta retry qilib "spam" qilmasin,
      // lekin logda error ko'rinadi.
      return new Response(`Error: ${e.message}`, { status: 500 });
    }
  },
};