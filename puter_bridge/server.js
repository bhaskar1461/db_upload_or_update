/**
 * Puter.js AI Bridge Server
 * Exposes a local OpenAI-compatible endpoint that proxies to Puter's free AI API.
 * Python script connects to http://localhost:3141/v1 — no API key needed!
 */

const express = require('express');
const { puter } = require('@heyputer/puter.js');

const app = express();
app.use(express.json());

const PORT = 3141;
const MODEL = 'gpt-5.4-nano'; // Free model via Puter

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', model: MODEL, provider: 'puter.js' });
});

// OpenAI-compatible chat completions endpoint
app.post('/v1/chat/completions', async (req, res) => {
    const { messages, temperature, max_tokens } = req.body;

    // Extract system and user content from messages array
    const systemMsg = messages.find(m => m.role === 'system');
    const userMsg = messages.find(m => m.role === 'user');

    const systemText = systemMsg ? systemMsg.content : '';
    const userText = userMsg ? userMsg.content : '';

    // Combine system + user into a single prompt for Puter
    const fullPrompt = systemText
        ? `${systemText}\n\n---\n\n${userText}`
        : userText;

    console.log(`[${new Date().toISOString()}] Generating for: ${userText.slice(0, 60)}...`);

    try {
        const response = await puter.ai.chat(fullPrompt, {
            model: MODEL,
            temperature: temperature ?? 0.2,
            max_tokens: max_tokens ?? 2048,
        });

        // Extract text — Puter returns either a string or object
        const text = typeof response === 'string'
            ? response
            : (response?.message?.content ?? response?.content ?? JSON.stringify(response));

        // Return in OpenAI-compatible format so our Python OpenAI client works as-is
        res.json({
            id: `puter-${Date.now()}`,
            object: 'chat.completion',
            model: MODEL,
            choices: [{
                index: 0,
                message: { role: 'assistant', content: text },
                finish_reason: 'stop',
            }],
            usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
        });

        console.log(`[OK] Response length: ${text.length} chars`);

    } catch (err) {
        console.error('[ERROR]', err.message);
        res.status(500).json({ error: { message: err.message, type: 'puter_error' } });
    }
});

app.listen(PORT, () => {
    console.log(`\n✅ Puter.js Bridge running at http://localhost:${PORT}`);
    console.log(`   Model: ${MODEL} (Free, no API key required)`);
    console.log(`   Python base_url: http://localhost:${PORT}/v1\n`);
});
