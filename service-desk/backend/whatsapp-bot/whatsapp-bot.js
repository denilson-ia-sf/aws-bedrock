const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

// Initialize WhatsApp client with local session storage to avoid scanning every time
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    }
});

// Generate QR Code in terminal for authentication
client.on('qr', (qr) => {
    console.log('🔄 Scan the QR Code below with your WhatsApp to connect the Agent:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('🚀 WhatsApp Agent is online and listening for messages!');
});

// Handle incoming messages
client.on('message', async (msg) => {
    // Avoid responding to group messages for this support scope
    if (msg.from.includes('@g.us')) return;

    console.log(`📩 Message received from ${msg.from}: ${msg.body}`);

    try {
        // Send user message to our Python FastAPI Backend Agent
        const response = await fetch('http://127.0.0', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: msg.body })
        });

        if (!response.ok) throw new Error('Backend communication failed');

        const data = await response.json();
        
        // Reply back directly on WhatsApp
        await msg.reply(data.reply);
        console.log(`📤 Reply sent back to ${msg.from}`);

    } catch (error) {
        console.error('❌ Error processing message:', error);
        await msg.reply('⚠️ Sorry, I encountered an internal error processing your request.');
    }
});

client.initialize();
