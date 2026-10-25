import assert from 'node:assert/strict';
import { guideDataFromMessage, textOfIncoming } from '../lib/ai/incoming-message';

const legacy = textOfIncoming({ role: 'user', content: 'substance' });
assert.equal(legacy, 'substance');

const parts = textOfIncoming({
  role: 'user',
  parts: [
    { type: 'text', text: 'Monadology' },
    { type: 'text', text: ' and substance' },
  ],
});
assert.equal(parts, 'Monadology and substance');

const fromStream = guideDataFromMessage({
  metadata: {
    mode: 'retrieval',
    sources: [{ title: 'Discourse on Metaphysics' }],
    suggestedFollowups: ['What is a monad?'],
    scope: 'discourse',
  },
});
assert.equal(fromStream?.mode, 'retrieval');
assert.equal(fromStream?.suggestedFollowups?.[0], 'What is a monad?');
assert.equal(guideDataFromMessage({ metadata: { note: 'no sources' } }), null);

console.log('chat-message-metadata: 4 assertions passed');
