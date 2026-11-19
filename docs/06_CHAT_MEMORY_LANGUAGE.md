# 06 — Chat, Memory, Conversation Continuity and Language

## Universal chat
- Multiple chats per user.
- Search, rename, archive and delete chats.
- Stream responses where supported.
- Support attachments subject to file policy.
- Regenerate or edit prompts where practical.
- Display provider/model and task status.
- Keep chat history private to the owner.

## Three separate context layers

### 1. Durable user memory
Long-term preferences or facts that are useful across chats. Save selectively, explain why where appropriate, and provide view/edit/disable/delete controls. Do not automatically store every message. Do not store sensitive information by default.

### 2. Project memory
Context specific to one project: objectives, decisions, files, project instructions, current status and milestones. Never leak project memory into unrelated projects unless the user explicitly shares it.

### 3. Conversation continuation summary
A temporary summary used when a conversation grows too long for the selected model context window. It is not the same as durable user memory.

## Automatic continuation behavior
1. Track token/context estimates for the selected model.
2. Use a configurable threshold with a safety margin; do not wait until context overflow.
3. Summarize the conversation into structured fields:
   - user goal and current question
   - key facts and decisions
   - user instructions/preferences relevant to this chat
   - completed work
   - pending tasks and next step
   - important file/artifact references
   - unresolved questions and uncertainties
4. Preserve the original conversation; never delete it to make a summary.
5. Create a linked continuation chat or continuation segment.
6. Carry forward the summary plus only the relevant recent messages and required project context.
7. Tell the user that the conversation is continuing from a summary, with an option to inspect it.
8. If summary generation fails, retry safely or ask the user to continue manually; do not silently lose context.
9. Version summaries and keep provenance to the source chat/messages.
10. Allow user to disable automatic continuation or manually start a continuation.

Do not promise that a summary preserves every detail. Retrieve original messages when a precise older detail is needed.

## Language behavior
- Detect the language of each user message.
- Reply in the same language and general register by default.
- Handle code-switching (e.g. Urdu + English, Hindi + English).
- Preserve technical names, code, identifiers and proper nouns.
- Support explicit language override at account and conversation level.
- Do not translate unless requested.
- Support right-to-left layout for Arabic and Urdu where possible.
- Test language detection with short messages, mixed scripts and ambiguous phrases.
- If uncertain, follow the user's latest explicit preference.

## Chat API concepts
- Create conversation.
- List/search conversations.
- Send message / stream response.
- Edit/regenerate message.
- Create continuation summary.
- Continue from summary.
- Read/update/delete memory.
- Read/update project context.
- Export/delete conversation.

## Privacy
Memory and summaries are user-owned data. Apply user authorization on every read/write. Include deletion/export policy and retention documentation. Never use one user's context to answer another user's query.
