import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "100vh",
            background: "#0b1120",
            color: "#f1f5f9",
            fontFamily: "monospace",
            padding: "2rem",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: "1rem",
          }}
        >
          <h1 style={{ color: "#ef4444", fontSize: "1.5rem" }}>
            ⚠️ Erro de renderização
          </h1>
          <pre
            style={{
              background: "#1a2540",
              padding: "1rem",
              borderRadius: "8px",
              maxWidth: "800px",
              overflow: "auto",
              fontSize: "0.875rem",
              whiteSpace: "pre-wrap",
            }}
          >
            {this.state.error?.toString()}
          </pre>
          {this.state.errorInfo?.componentStack && (
            <pre
              style={{
                background: "#121a2e",
                padding: "1rem",
                borderRadius: "8px",
                maxWidth: "800px",
                overflow: "auto",
                fontSize: "0.75rem",
                color: "#94a3b8",
                whiteSpace: "pre-wrap",
              }}
            >
              {this.state.errorInfo.componentStack}
            </pre>
          )}
          <button
            onClick={() => window.location.reload()}
            style={{
              background: "#2563eb",
              color: "#fff",
              border: "none",
              padding: "0.5rem 1rem",
              borderRadius: "6px",
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            Recarregar página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
