"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = require("vscode");
const antigravity_sdk_1 = require("antigravity-sdk");
const client_bedrock_runtime_1 = require("@aws-sdk/client-bedrock-runtime");
async function activate(context) {
    console.log('Congratulations, your extension "my-antigravity-extension" is now active!');
    // Initialize the SDK
    const sdk = new antigravity_sdk_1.AntigravitySDK(context);
    await sdk.initialize();
    // 1. Create a custom UI integration in the Agent View
    const ui = new antigravity_sdk_1.IntegrationManager();
    ui.addTopBarButton('hello_btn', '👋', 'Say Hello', {
        title: 'Greeting',
        rows: [{ key: 'Status:', value: 'Extension Active' }]
    });
    await ui.install();
    ui.enableAutoRepair(); // Survives Antigravity updates
    // 2. Register a basic command
    let disposable = vscode.commands.registerCommand('my-antigravity-extension.helloWorld', async () => {
        const prefs = await sdk.cascade.getPreferences();
        vscode.window.showInformationMessage(`Hello World from Antigravity Extension! (Terminal Policy: ${prefs.terminalExecutionPolicy})`);
    });
    // 3. Register Bedrock Command
    let bedrockDisposable = vscode.commands.registerCommand('my-antigravity-extension.askBedrock', async () => {
        const config = vscode.workspace.getConfiguration('bedrock');
        const accessKeyId = config.get('accessKeyId');
        const secretAccessKey = config.get('secretAccessKey');
        const region = config.get('region') || 'us-east-1';
        const modelId = config.get('modelId') || 'anthropic.claude-3-opus-20240229-v1:0';
        if (!accessKeyId || !secretAccessKey) {
            vscode.window.showErrorMessage('Please configure your AWS Access Key and Secret Key in settings (search for "Bedrock").');
            return;
        }
        const prompt = await vscode.window.showInputBox({ prompt: 'What would you like to ask Bedrock?' });
        if (!prompt)
            return;
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Asking Bedrock (${modelId})...`,
            cancellable: false
        }, async () => {
            try {
                const client = new client_bedrock_runtime_1.BedrockRuntimeClient({
                    region,
                    credentials: { accessKeyId, secretAccessKey }
                });
                // Formatting payload for Claude 3 Messages API
                const payload = {
                    anthropic_version: "bedrock-2023-05-31",
                    max_tokens: 2000,
                    messages: [
                        { role: "user", content: prompt }
                    ]
                };
                const command = new client_bedrock_runtime_1.InvokeModelCommand({
                    modelId,
                    contentType: "application/json",
                    accept: "application/json",
                    body: JSON.stringify(payload)
                });
                const response = await client.send(command);
                const responseBody = JSON.parse(new TextDecoder().decode(response.body));
                const replyText = responseBody.content?.[0]?.text || 'No response text';
                // Show in a new text document tab
                const doc = await vscode.workspace.openTextDocument({ content: replyText, language: 'markdown' });
                vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
            }
            catch (err) {
                vscode.window.showErrorMessage(`Bedrock Error: ${err.message}`);
            }
        });
    });
    // 4. Monitor agent activity in real time
    sdk.monitor.onStepCountChanged((e) => {
        console.log(`Agent ${e.title} advanced to step ${e.newCount}`);
    });
    sdk.monitor.start();
    // Cleanup on deactivate
    context.subscriptions.push(sdk);
    context.subscriptions.push(disposable);
    context.subscriptions.push(bedrockDisposable);
}
function deactivate() { }
//# sourceMappingURL=extension.js.map