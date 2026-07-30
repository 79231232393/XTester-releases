# XTester

XTester is a local Windows desktop application and local MCP server for writing, compiling, and historically testing crypto trading strategies in C#.

- Website: <https://xtester.pw>
- Latest stable release: <https://github.com/79231232393/XTester-releases/releases/latest>

This repository hosts the public release artifacts. Application updates are delivered from here.

## What XTester is

XTester runs entirely as a desktop application on your own Windows machine. It combines:

- a C# strategy editor with IntelliSense, diagnostics, and Roslyn compilation;
- a historical simulation engine for spot and USDT-margined futures markets;
- a market-data manager that downloads and stores 1-minute candle history locally;
- statistics, charting, and trade-level reporting for completed runs;
- a local MCP server, so an MCP-capable AI client can drive the same functionality programmatically.

Strategies are ordinary C# classes compiled against a documented strategy API. Projects, strategy sources, saved
versions, and downloaded market data are stored in local files under your user profile's application-data folder.

## Why use it for strategy testing

- **Exchange-realistic simulation.** Runs are driven by downloaded exchange history rather than synthetic prices, and
  the engine models maker/taker fees, funding payments, margin, and liquidation behavior for the markets where those
  mechanics are supported.
- **Reproducible runs.** The same project and the same stored history produce the same result, which is what makes a
  comparison between two strategy versions meaningful.
- **Validation on data the strategy was not tuned on.** Walk-forward analysis splits the tested period into
  in-sample and out-of-sample windows so a result can be checked against fresh data instead of the fitting window.
- **Version history.** Strategy versions and specifications are snapshotted inside the project, so a change can be
  compared against, or rolled back to, an earlier state.
- **Interactive inspection.** A run can be stepped bar by bar and paused at a chosen simulation time to inspect
  positions, orders, indicator values, and the strategy's own log.

XTester is a testing and research tool. It does not predict markets and makes no claim about the future profitability
of any strategy.

## MCP integration

XTester ships a local [Model Context Protocol](https://modelcontextprotocol.io) server that runs on your machine and
communicates over stdio. There is no hosted or remote XTester MCP endpoint: the server is a process started by your
MCP client on the same computer, and it acts only on the local XTester project you bind it to.

Through MCP, an AI client can read and edit strategy sources, compile them, download market history, run backtests
and interactive simulations, read statistics and rendered charts, and work with the project's version history.

The MCP server exposes a single tool catalog. Every tool carries the standard MCP annotations
(`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`). Those annotations are advisory hints that
describe intent — they are not proof that anything is enforced. What actually protects an operation is its own input
schema and the runtime checks the application performs when the operation is invoked, which differ per operation.

- MCP overview: <https://xtester.pw/mcp>
- Setup instructions: <https://xtester.pw/mcp/install>
- Tool reference: <https://xtester.pw/mcp/tools>
- Usage examples: <https://xtester.pw/mcp/examples>
- Security model: <https://xtester.pw/mcp/security>

## Installation

1. Download the installer from the [latest stable release](https://github.com/79231232393/XTester-releases/releases/latest).
2. Run it and follow the installer.
3. Start XTester from the Start menu.

Using XTester locally does not require creating an account. Signing in is needed only for the optional cloud project
features. Configuring MCP for your AI client is described at <https://xtester.pw/mcp/install>.

## Documentation

- Product documentation and guides: <https://xtester.pw>
- MCP documentation: <https://xtester.pw/mcp>
- In-application help: the **Help** section inside XTester, which is installed with the application and covers the
  editor, simulator, market data, and MCP setup.

## Security and data handling

- **Local by default.** Projects, strategy sources, downloaded market data, and application settings live on your
  machine, not in a hosted account.
- **Network access is feature-driven.** XTester makes network requests for the features that inherently need them:
  downloading exchange market history and symbol/funding metadata, calling AI providers you configure, checking for
  application updates, and — if you set them up — reaching an exchange for live or paper execution. Which of these
  happen depends on what you use.
- **Credentials are stored locally.** Exchange API keys and AI provider keys you enter are kept in your user profile
  and are not returned by MCP tools or shown in diagnostics. A credential is sent only to the external service you
  explicitly configured it for, and only when that service requires authentication.
- **Telemetry is opt-in.** Diagnostic telemetry is disabled unless you explicitly allow it, and it never carries
  strategy code, prompts, AI responses, credentials, balances, positions, orders, or file contents.
- **Trading is explicit.** Historical testing never touches an exchange account. Real-money execution is a separate,
  deliberately gated part of the product and is not a side effect of running a backtest.

Details, including the MCP boundary and what each tool can reach, are documented at <https://xtester.pw/mcp/security>.

## Releases and updates

- Every release is published in this repository as a tagged GitHub Release with its installer and update packages.
- Installed builds check this repository for newer versions and can apply a delta update from inside the application.
- Release notes for each version are attached to its GitHub Release.
- Always refer to the [latest stable release](https://github.com/79231232393/XTester-releases/releases/latest) rather
  than to a fixed version number.

## Requirements

- Windows 10 (version 2004, build 19041) or Windows 11
- x64 processor
- An internet connection for downloading market history, updates, and any AI provider or exchange features you use

The application is self-contained: the required .NET runtime is included in the installer.

---

XTester is developed by Elinesoft. For product information and contact details, see <https://xtester.pw>.
