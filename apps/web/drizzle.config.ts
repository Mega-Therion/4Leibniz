import { defineConfig } from 'drizzle-kit';
import 'dotenv/config';

export default defineConfig({
  dialect: 'postgresql',
  schema: './lib/db/schema.ts',
  out: './drizzle',
  dbCredentials: {
    url: process.env.POSTGRES_URL!,
  },
  strict: true,
  verbose: true,
});
