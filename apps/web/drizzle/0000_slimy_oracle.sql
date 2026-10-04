CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS "chat_messages" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"session_id" uuid NOT NULL,
	"role" text NOT NULL,
	"content" text NOT NULL,
	"mode" text,
	"sources" jsonb,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "chat_sessions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"work_slug" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "chunk_entities" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"chunk_id" uuid NOT NULL,
	"entity_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "dossier_entries" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"kind" text NOT NULL,
	"slug" text NOT NULL,
	"title" text NOT NULL,
	"text" text NOT NULL,
	"metadata" jsonb,
	"embedding" vector(1536) NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "entities" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"name" text NOT NULL,
	"kind" text DEFAULT 'person' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "entities_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "themes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"label" text NOT NULL,
	"description" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "themes_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "timeline_events" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"year" integer NOT NULL,
	"date_label" text NOT NULL,
	"title" text NOT NULL,
	"description" text NOT NULL,
	"category" text DEFAULT 'life' NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "timeline_events_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "work_chunks" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"work_id" uuid NOT NULL,
	"section_id" uuid,
	"anchor" text NOT NULL,
	"text" text NOT NULL,
	"excerpt" text NOT NULL,
	"embedding" vector(1536) NOT NULL,
	"char_count" integer NOT NULL,
	"token_estimate" integer NOT NULL,
	"language" text DEFAULT 'en' NOT NULL,
	"quality_score" real DEFAULT 0.9 NOT NULL,
	"citation_label" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "work_sections" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"work_id" uuid NOT NULL,
	"anchor" text NOT NULL,
	"label" text NOT NULL,
	"title" text,
	"position" integer NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "work_themes" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"work_id" uuid NOT NULL,
	"theme_id" uuid NOT NULL
);
--> statement-breakpoint
CREATE TABLE IF NOT EXISTS "works" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"slug" text NOT NULL,
	"title" text NOT NULL,
	"alt_title" text,
	"summary" text DEFAULT '' NOT NULL,
	"language" text DEFAULT 'en' NOT NULL,
	"original_language" text,
	"status" text DEFAULT 'in-progress' NOT NULL,
	"date_label" text,
	"date_start" integer,
	"date_end" integer,
	"source_note" text,
	"editorial_note" text,
	"featured" boolean DEFAULT false NOT NULL,
	"published" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "works_slug_unique" UNIQUE("slug")
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "chat_messages" ADD CONSTRAINT "chat_messages_session_id_chat_sessions_id_fk" FOREIGN KEY ("session_id") REFERENCES "public"."chat_sessions"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "chunk_entities" ADD CONSTRAINT "chunk_entities_chunk_id_work_chunks_id_fk" FOREIGN KEY ("chunk_id") REFERENCES "public"."work_chunks"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "chunk_entities" ADD CONSTRAINT "chunk_entities_entity_id_entities_id_fk" FOREIGN KEY ("entity_id") REFERENCES "public"."entities"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "work_chunks" ADD CONSTRAINT "work_chunks_work_id_works_id_fk" FOREIGN KEY ("work_id") REFERENCES "public"."works"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "work_chunks" ADD CONSTRAINT "work_chunks_section_id_work_sections_id_fk" FOREIGN KEY ("section_id") REFERENCES "public"."work_sections"("id") ON DELETE set null ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "work_sections" ADD CONSTRAINT "work_sections_work_id_works_id_fk" FOREIGN KEY ("work_id") REFERENCES "public"."works"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "work_themes" ADD CONSTRAINT "work_themes_work_id_works_id_fk" FOREIGN KEY ("work_id") REFERENCES "public"."works"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "work_themes" ADD CONSTRAINT "work_themes_theme_id_themes_id_fk" FOREIGN KEY ("theme_id") REFERENCES "public"."themes"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "chat_messages_session_idx" ON "chat_messages" USING btree ("session_id");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "chunk_entities_unique" ON "chunk_entities" USING btree ("chunk_id","entity_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "chunk_entities_chunk_idx" ON "chunk_entities" USING btree ("chunk_id");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "dossier_entries_kind_slug" ON "dossier_entries" USING btree ("kind","slug");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "work_chunks_work_idx" ON "work_chunks" USING btree ("work_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "work_sections_work_idx" ON "work_sections" USING btree ("work_id");--> statement-breakpoint
CREATE UNIQUE INDEX IF NOT EXISTS "work_themes_unique" ON "work_themes" USING btree ("work_id","theme_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "work_themes_work_idx" ON "work_themes" USING btree ("work_id");

-- ─── pgvector HNSW indexes (cosine distance retrieval) ────────────────────
CREATE INDEX IF NOT EXISTS work_chunks_embedding_hnsw
  ON work_chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS dossier_entries_embedding_hnsw
  ON dossier_entries USING hnsw (embedding vector_cosine_ops);
