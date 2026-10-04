import {
  boolean,
  customType,
  index,
  integer,
  jsonb,
  pgTable,
  real,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from 'drizzle-orm/pg-core';

/** pgvector column — requires `CREATE EXTENSION IF NOT EXISTS vector;` */
export const embeddingVector = customType<{
  data: number[];
  driverData: string;
  config: { dimension: number };
}>({
  dataType(config) {
    return config ? `vector(${config.dimension})` : 'vector';
  },
  toDriver(value) {
    return JSON.stringify(value);
  },
});

export const works = pgTable('works', {
  id: uuid('id').primaryKey().defaultRandom(),
  slug: text('slug').notNull().unique(),
  title: text('title').notNull(),
  altTitle: text('alt_title'),
  summary: text('summary').notNull().default(''),
  language: text('language').notNull().default('en'),
  originalLanguage: text('original_language'),
  status: text('status').notNull().default('in-progress'),
  dateLabel: text('date_label'),
  dateStart: integer('date_start'),
  dateEnd: integer('date_end'),
  sourceNote: text('source_note'),
  editorialNote: text('editorial_note'),
  featured: boolean('featured').notNull().default(false),
  published: boolean('published').notNull().default(true),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
});

export const workSections = pgTable(
  'work_sections',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workId: uuid('work_id')
      .notNull()
      .references(() => works.id, { onDelete: 'cascade' }),
    anchor: text('anchor').notNull(),
    label: text('label').notNull(),
    title: text('title'),
    position: integer('position').notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index('work_sections_work_idx').on(t.workId)],
);

export const workChunks = pgTable(
  'work_chunks',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workId: uuid('work_id')
      .notNull()
      .references(() => works.id, { onDelete: 'cascade' }),
    sectionId: uuid('section_id').references(() => workSections.id, {
      onDelete: 'set null',
    }),
    anchor: text('anchor').notNull(),
    text: text('text').notNull(),
    excerpt: text('excerpt').notNull(),
    embedding: embeddingVector('embedding', { dimension: 1536 }).notNull(),
    charCount: integer('char_count').notNull(),
    tokenEstimate: integer('token_estimate').notNull(),
    language: text('language').notNull().default('en'),
    qualityScore: real('quality_score').notNull().default(0.9),
    citationLabel: text('citation_label'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index('work_chunks_work_idx').on(t.workId)],
);

export const themes = pgTable('themes', {
  id: uuid('id').primaryKey().defaultRandom(),
  slug: text('slug').notNull().unique(),
  label: text('label').notNull(),
  description: text('description'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const workThemes = pgTable(
  'work_themes',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    workId: uuid('work_id')
      .notNull()
      .references(() => works.id, { onDelete: 'cascade' }),
    themeId: uuid('theme_id')
      .notNull()
      .references(() => themes.id, { onDelete: 'cascade' }),
  },
  (t) => [
    uniqueIndex('work_themes_unique').on(t.workId, t.themeId),
    index('work_themes_work_idx').on(t.workId),
  ],
);

export const entities = pgTable('entities', {
  id: uuid('id').primaryKey().defaultRandom(),
  slug: text('slug').notNull().unique(),
  name: text('name').notNull(),
  kind: text('kind').notNull().default('person'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const chunkEntities = pgTable(
  'chunk_entities',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    chunkId: uuid('chunk_id')
      .notNull()
      .references(() => workChunks.id, { onDelete: 'cascade' }),
    entityId: uuid('entity_id')
      .notNull()
      .references(() => entities.id, { onDelete: 'cascade' }),
  },
  (t) => [
    uniqueIndex('chunk_entities_unique').on(t.chunkId, t.entityId),
    index('chunk_entities_chunk_idx').on(t.chunkId),
  ],
);

/** Editorial dossier — biography, timeline, concepts, correspondents, themes. */
export const dossierEntries = pgTable(
  'dossier_entries',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    kind: text('kind').notNull(),
    slug: text('slug').notNull(),
    title: text('title').notNull(),
    text: text('text').notNull(),
    metadata: jsonb('metadata'),
    embedding: embeddingVector('embedding', { dimension: 1536 }).notNull(),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [uniqueIndex('dossier_entries_kind_slug').on(t.kind, t.slug)],
);

export const timelineEvents = pgTable('timeline_events', {
  id: uuid('id').primaryKey().defaultRandom(),
  slug: text('slug').notNull().unique(),
  year: integer('year').notNull(),
  dateLabel: text('date_label').notNull(),
  title: text('title').notNull(),
  description: text('description').notNull(),
  category: text('category').notNull().default('life'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const chatSessions = pgTable('chat_sessions', {
  id: uuid('id').primaryKey().defaultRandom(),
  workSlug: text('work_slug'),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
});

export const chatMessages = pgTable(
  'chat_messages',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    sessionId: uuid('session_id')
      .notNull()
      .references(() => chatSessions.id, { onDelete: 'cascade' }),
    role: text('role').notNull(),
    content: text('content').notNull(),
    mode: text('mode'),
    sources: jsonb('sources'),
    createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [index('chat_messages_session_idx').on(t.sessionId)],
);
