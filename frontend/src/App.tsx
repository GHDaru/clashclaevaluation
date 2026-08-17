import { useState, useCallback } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api/client";
import Landing from "./pages/Landing";
import PlayerLookup from "./pages/PlayerLookup";
import Dashboard from "./pages/Dashboard";
import ConfigPanel from "./pages/ConfigPanel";
import PlayerDetail from "./pages/PlayerDetail";
import { Layout } from "./components/Layout";
import { ToastProvider, useToast } from "./components/Toast";
import { SkeletonCard } from "./components/Skeleton";
import { Button } from "./components/Button";
import { Card } from "./components/Card";
import { Icon } from "./components/Icon";
import type { ClanStatusDTO } from "./types/domain";

type Page = "landing" | "playerLookup" | "dashboard" | "config" | "player";

function AppContent() {
  const [page, setPage] = useState<Page>("landing");
  const [selectedPlayer, setSelectedPlayer] = useState<string>("");
  const queryClient = useQueryClient();
  const toast = useToast();

  const { data, isLoading, error } = useQuery<ClanStatusDTO>({
    queryKey: ["clanStatus"],
    queryFn: api.getClanStatus,
    enabled: page === "dashboard" || page === "config",
  });

  const evalMutation = useMutation({
    mutationFn: () => api.triggerEvaluation(),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["clanStatus"] });
      toast.success(
        `Avaliação concluída: ${result.players_evaluated} jogadores · ${result.summary?.critical ?? 0} críticos`
      );
    },
    onError: () => {
      toast.error("Erro ao avaliar o clã. Verifique a configuração.");
    },
  });

  const navigate = useCallback((newPage: Page) => {
    if (typeof document !== "undefined" && "startViewTransition" in document) {
      (document as Document & { startViewTransition: (cb: () => void) => void }).startViewTransition(() => {
        setPage(newPage);
      });
    } else {
      setPage(newPage);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, []);

  const handlePlayerClick = (tag: string) => {
    setSelectedPlayer(tag);
    navigate("player");
  };

  const handlePlayerLookup = (tag: string) => {
    setSelectedPlayer(tag);
    navigate("player");
  };

  const goHome = () => navigate("landing");

  // --- Landing page ---
  if (page === "landing") {
    return (
      <Layout
        onEvaluate={() => navigate("dashboard")}
        onConfig={() => navigate("dashboard")}
        evaluating={false}
        showConfig={true}
        onHome={goHome}
      >
        <Landing
          onClanView={() => navigate("dashboard")}
          onPlayerView={() => navigate("playerLookup")}
        />
      </Layout>
    );
  }

  // --- Player Lookup page ---
  if (page === "playerLookup") {
    return (
      <Layout
        onEvaluate={() => navigate("dashboard")}
        onConfig={() => navigate("dashboard")}
        evaluating={false}
        showConfig={true}
        onHome={goHome}
      >
        <PlayerLookup
          onSubmit={handlePlayerLookup}
          onBack={() => navigate("landing")}
        />
      </Layout>
    );
  }

  // --- Player Detail page ---
  if (page === "player") {
    return (
      <Layout
        onEvaluate={() => evalMutation.mutate()}
        onConfig={() => navigate("config")}
        evaluating={evalMutation.isPending}
        showConfig={false}
        onBack={() => navigate("dashboard")}
        onHome={goHome}
      >
        <PlayerDetail playerTag={selectedPlayer} onBack={() => navigate("dashboard")} />
      </Layout>
    );
  }

  // --- Config page ---
  if (page === "config") {
    return (
      <Layout
        onEvaluate={() => evalMutation.mutate()}
        onConfig={() => navigate("config")}
        evaluating={evalMutation.isPending}
        showConfig={true}
        onBack={() => navigate("dashboard")}
        onHome={goHome}
      >
        <ConfigPanel />
      </Layout>
    );
  }

  // --- Dashboard page ---
  if (isLoading) {
    return (
      <Layout
        onEvaluate={() => evalMutation.mutate()}
        onConfig={() => navigate("config")}
        evaluating={evalMutation.isPending}
        showConfig={false}
        onHome={goHome}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout
        onEvaluate={() => evalMutation.mutate()}
        onConfig={() => navigate("config")}
        evaluating={evalMutation.isPending}
        showConfig={false}
        onHome={goHome}
      >
        <Card className="p-8 text-center">
          <div className="flex flex-col items-center gap-4">
            <Icon name="alert" size={48} className="text-[var(--color-danger)]" />
            <div>
              <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-1">
                Erro ao carregar dados
              </h2>
              <p className="text-sm text-[var(--color-text-secondary)]">
                Verifique se o backend está rodando e se a tag do clã está configurada.
              </p>
            </div>
            <Button variant="primary" iconLeft="cog" onClick={() => navigate("config")}>
              Abrir Configuração
            </Button>
          </div>
        </Card>
      </Layout>
    );
  }

  return (
    <Layout
      onEvaluate={() => evalMutation.mutate()}
      onConfig={() => navigate("config")}
      evaluating={evalMutation.isPending}
      showConfig={false}
      onHome={goHome}
    >
      <Dashboard
        data={data ?? { war_active: false, war_id: null, day: null, day_label: null, status: null, position: null, total_fame: 0, daily_fame: 0, clans_count: 0, relaxed: false, players: [] }}
        onPlayerClick={handlePlayerClick}
      />
    </Layout>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}
