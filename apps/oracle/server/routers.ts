import { z } from "zod";
import { COOKIE_NAME } from "../shared/const.js";
import { getSessionCookieOptions } from "./_core/cookies";
import { invokeLLM } from "./_core/llm";
import { protectedProcedure, publicProcedure, router } from "./_core/trpc";
import { systemRouter } from "./_core/systemRouter";
import { getSavedInsightSync, upsertSavedInsightSync } from "./db";
import { formalClaims, statusLabel } from "../shared/formal-claims.js";

const repoContext = `You are the Leibniz Oracle, a careful guide to the Mega-Therion/4Leibniz repository and the philosophy behind it.

Repository facts from the README:
- 4Leibniz is a Lean 4 formal laboratory with a Python claim-to-kernel pipeline called calculemus.py.
- The formal-claims catalog is the authoritative source for current theorem/module claim facts; do not rely on dated counts copied from the README or another snapshot.
- The pipeline is natural-language claim -> Universal Calculus IR and fingerprint -> transparent proof search -> Lean theorem synthesis -> kernel verification -> append-only adjudication ledger.
- The flagship sufficient-reason transitivity example is described as kernel-proven with zero sorry and zero new axioms.
- The README explicitly warns that Harmonia contains a tautological definition harmonia_stabilis u gamma := u >= gamma, where anti_drift_preservation simply returns its hypothesis. It also contains axioms. This compiles but does not establish a physical coherence theorem.
- The README explicitly warns that Calculemus.execute_calculemus is a hand-written VeritasReceipt literal, not a measurement. For real figures users should run scripts/measure_kernel.py --check.
- A companion anti-drift analysis says a non-monotonic coherence quantity cannot yield an iff threshold gate; treat this as an important caution when discussing Harmonia.

Answer in a warm, intellectually curious voice. Distinguish clearly between historical interpretation, what the repository claims, what Lean's kernel checks, and what remains an axiom/open measurement. Never invent files, theorem names, test results, or numerical facts outside this context. When a Formal claims catalog section is provided, you may explain any listed claim, but you may call something "formally verified" or "proved" ONLY when its status label says "Formally verified (Lean)"; conditional claims must mention what they depend on, and open problems must never be described as established. If asked about something unrelated to the repo or Leibniz, say you can help with the website and its subject area but do not pretend to know the page's private state. Prefer concise paragraphs and occasional short lists. Do not use markdown tables.`;

const messageSchema = z.object({ role: z.enum(["user", "assistant"]), content: z.string().min(1).max(2000) });
const fallbackProfile = { domain: "mixed", concepts: ["general question"], task: "explain", difficulty: "intermediate", needsCaveat: false };

type QueryProfile = typeof fallbackProfile;

function textFromResponse(response: Awaited<ReturnType<typeof invokeLLM>>) {
  const raw = response.choices?.[0]?.message?.content;
  return typeof raw === "string" ? raw : Array.isArray(raw) ? raw.map((part) => typeof part === "string" ? part : "text" in part ? part.text : "").join("") : "";
}

async function understandQuery(question: string): Promise<QueryProfile> {
  try {
    const response = await invokeLLM({
      messages: [
        { role: "system", content: "Classify a user's question for a Leibniz philosophy and Lean repository tutor. Return JSON only with keys domain, concepts, task, difficulty, and needsCaveat. Domain must be metaphysics, epistemology, logic, physics, history, repository, or mixed. Task must be explain, compare, trace, critique, locate, or apply. Difficulty must be beginner, intermediate, or advanced. concepts must be a short string array." },
        { role: "user", content: question },
      ],
      response_format: { type: "json_object" },
    });
    const parsed = JSON.parse(textFromResponse(response)) as Partial<QueryProfile>;
    return {
      domain: typeof parsed.domain === "string" ? parsed.domain : fallbackProfile.domain,
      concepts: Array.isArray(parsed.concepts) ? parsed.concepts.slice(0, 4).map(String) : fallbackProfile.concepts,
      task: typeof parsed.task === "string" ? parsed.task : fallbackProfile.task,
      difficulty: typeof parsed.difficulty === "string" ? parsed.difficulty : fallbackProfile.difficulty,
      needsCaveat: Boolean(parsed.needsCaveat),
    };
  } catch {
    return fallbackProfile;
  }
}

function suggestedFollowUps(profile: QueryProfile) {
  const concept = profile.concepts[0] ?? "this idea";
  const byDomain: Record<string, string[]> = {
    metaphysics: [`How does ${concept} relate to monads?`, "What would Leibniz say is the sufficient reason here?", "Where does the repository formalize this idea?"],
    epistemology: ["What counts as evidence in the 4Leibniz project?", "How is a proof different from an interpretation?", "Can you show me the relevant caveat in the README?"],
    logic: ["Can you translate this into the claim-to-kernel pipeline?", "Which part could Lean actually check?", "What would make this claim undecidable?"],
    physics: ["Which parts are axioms rather than physical results?", "How does the Harmonia caveat apply here?", "What should be measured outside the formal model?"],
    history: ["How does this connect to Leibniz's original writings?", "What is historical interpretation versus formal reconstruction?", "Which repository module carries this theme?"],
    repository: ["Which file should I open first?", "What does the kernel really verify in this example?", "Can you trace the claim through calculemus.py?"],
    mixed: [`Can you connect ${concept} to a repository module?`, "What is the strongest caveat or limitation?", "Can you explain this at a beginner level?"],
  };
  return byDomain[profile.domain] ?? byDomain.mixed;
}

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query((opts) => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),
  }),
  health: publicProcedure.query(() => ({ status: "ok" })),
  /**
   * 4Leibniz formal-claims catalog, contract v1 (issue #11). READ-ONLY:
   * queries only. The Oracle consumes the packaged snapshot; it never
   * produces or mutates claim statuses. `formally_verified` is true only
   * for catalog entries whose status is `proved`.
   */
  formalClaims: router({
    list: publicProcedure.query(() => {
      const claims = formalClaims.listClaims();
      return {
        schema_version: formalClaims.catalog.schema_version,
        source: formalClaims.catalog.source,
        claims: claims.map((c) => ({
          claim_id: c.claim_id,
          title: c.title,
          module: c.module,
          status: c.status,
          status_label: statusLabel(c.status),
          formally_verified: c.status === "proved",
          human_summary: c.human_summary,
        })),
      } as const;
    }),
    byId: publicProcedure
      .input(z.object({ claim_id: z.string().min(1).max(200) }))
      .query(({ input }) => {
        const display = formalClaims.describeClaim(input.claim_id);
        if (!display) return { found: false as const, claim: null };
        return { found: true as const, claim: display };
      }),
  }),
  insights: router({
    pull: protectedProcedure.query(async ({ ctx }) => {
      const record = await getSavedInsightSync(ctx.user.openId);
      return { payload: record?.payload ?? null, updatedAt: record?.updatedAt ?? null };
    }),
    push: protectedProcedure.input(z.object({ payload: z.string().max(500000) })).mutation(async ({ ctx, input }) => {
      await upsertSavedInsightSync({ userOpenId: ctx.user.openId, payload: input.payload });
      return { success: true, updatedAt: new Date() } as const;
    }),
  }),
  oracle: router({
    chat: publicProcedure.input(z.object({ messages: z.array(messageSchema).min(1).max(12) })).mutation(async ({ input }) => {
      const latestQuestion = [...input.messages].reverse().find((message) => message.role === "user")?.content ?? "";
      const profile = await understandQuery(latestQuestion);
      // 4Leibniz catalog v1 (issue #11): catalog-grounded formal claims.
      // Sourced explanation vs. formally verified proof is separated by the
      // status label; the model is instructed to use it exactly.
      const matchedClaims = formalClaims
        .matchClaimsInText(latestQuestion)
        .slice(0, 5)
        .map((c) => {
          const d = formalClaims.describeClaim(c.claim_id)!;
          return `- [${d.status_label}] ${d.title} (${d.module}) — ${d.sourced_explanation}`;
        })
        .join("\n");
      const claimsSection =
        matchedClaims.length > 0
          ? `\n\nFormal claims catalog (proof-grounded, commit ${formalClaims.catalog.source.commit.slice(0, 12)}):\n${matchedClaims}\nUse each claim's status label verbatim when discussing verification.`
          : "";
      const answer = await invokeLLM({
        messages: [
          { role: "system", content: `${repoContext}${claimsSection}\n\nQuery interpretation layer:\n- Domain: ${profile.domain}\n- Concepts: ${profile.concepts.join(", ")}\n- Task: ${profile.task}\n- Difficulty: ${profile.difficulty}\n- Add an explicit caveat about evidence and interpretation: ${profile.needsCaveat ? "yes" : "only if relevant"}\n\nUse this profile to structure the answer. Start with the direct answer, then connect it to the repo or Leibniz, and end with one useful next question when the topic is complex.` },
          ...input.messages.map((message) => ({ role: message.role, content: message.content })),
        ],
      });
      return { answer: textFromResponse(answer), profile, followUps: suggestedFollowUps(profile) };
    }),
  }),
});

export type AppRouter = typeof appRouter;
