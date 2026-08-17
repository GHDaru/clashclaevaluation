import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import type { ConfigDTO, ConfigUpdateDTO } from "../types/domain";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { ToggleSwitch } from "../components/ToggleSwitch";
import { Modal } from "../components/Modal";
import { Skeleton } from "../components/Skeleton";
import { useToast } from "../components/Toast";
import { Icon, type IconName } from "../components/Icon";

const INPUT_CLASS =
  "block w-full bg-[var(--color-surface-1)] border border-[var(--color-border)] rounded-[var(--radius-sm)] px-3 py-2 text-[var(--color-text-primary)] text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)] focus-visible:border-[var(--color-primary)] transition-colors placeholder:text-[var(--color-text-tertiary)]";

function SectionCard({
  title,
  icon,
  children,
}: {
  title: string;
  icon: IconName;
  children: React.ReactNode;
}) {
  return (
    <Card className="p-5">
      <div className="flex items-center gap-2 mb-4">
        <Icon name={icon} size={18} className="text-[var(--color-accent)]" />
        <h2 className="text-lg font-bold text-[var(--color-text-primary)]">{title}</h2>
      </div>
      {children}
    </Card>
  );
}

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-sm text-[var(--color-text-secondary)] font-medium">{label}</span>
      <div className="mt-1.5">{children}</div>
      {hint && (
        <span className="text-xs text-[var(--color-text-tertiary)] mt-1 block">{hint}</span>
      )}
    </label>
  );
}

export default function ConfigPanel() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const { data: config, isLoading } = useQuery<ConfigDTO>({
    queryKey: ["config"],
    queryFn: api.getConfig,
  });

  const [form, setForm] = useState<ConfigUpdateDTO>({});
  const [showConfirm, setShowConfirm] = useState(false);

  const updateMutation = useMutation({
    mutationFn: (update: ConfigUpdateDTO) => api.updateConfig(update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config"] });
      queryClient.invalidateQueries({ queryKey: ["clanStatus"] });
      toast.success("Configuração salva com sucesso!");
      setForm({});
    },
    onError: () => {
      toast.error("Erro ao salvar configuração.");
    },
  });

  const defaultsMutation = useMutation({
    mutationFn: () => api.restoreDefaults(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["config"] });
      queryClient.invalidateQueries({ queryKey: ["clanStatus"] });
      toast.success("Defaults restaurados!");
      setForm({});
      setShowConfirm(false);
    },
    onError: () => {
      toast.error("Erro ao restaurar defaults.");
    },
  });

  if (isLoading || !config) {
    return (
      <div className="max-w-2xl mx-auto space-y-4">
        <Skeleton className="h-10 w-48 rounded-[var(--radius-lg)]" />
        <Skeleton className="h-40 w-full rounded-[var(--radius-lg)]" />
        <Skeleton className="h-48 w-full rounded-[var(--radius-lg)]" />
        <Skeleton className="h-40 w-full rounded-[var(--radius-lg)]" />
      </div>
    );
  }

  const current = { ...config, ...form };
  const hasChanges = Object.keys(form).length > 0;

  const handleSave = () => {
    updateMutation.mutate(form);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
        Configuração de Regras
      </h1>

      {/* Clan Tag */}
      <SectionCard title="Clã" icon="shield">
        <Field label="Tag do Clã">
          <input
            type="text"
            value={current.cr_clan_tag || ""}
            onChange={(e) => setForm({ ...form, cr_clan_tag: e.target.value })}
            placeholder="#ABC123…"
            className={INPUT_CLASS}
            autoComplete="off"
            spellCheck={false}
          />
        </Field>
      </SectionCard>

      {/* Card Thresholds */}
      <SectionCard title="Thresholds de Cartões" icon="card-yellow">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Field label="Ataques por dia">
            <input
              type="number"
              min={1}
              max={4}
              value={current.attacks_per_day ?? 4}
              onChange={(e) => setForm({ ...form, attacks_per_day: Number(e.target.value) })}
              className={INPUT_CLASS}
            />
          </Field>
          <Field label="Amarelo → Vermelho">
            <input
              type="number"
              min={2}
              value={current.yellow_to_red ?? 4}
              onChange={(e) => setForm({ ...form, yellow_to_red: Number(e.target.value) })}
              className={INPUT_CLASS}
            />
          </Field>
          <Field label="Vermelho → Preto">
            <input
              type="number"
              min={2}
              value={current.red_to_black ?? 4}
              onChange={(e) => setForm({ ...form, red_to_black: Number(e.target.value) })}
              className={INPUT_CLASS}
            />
          </Field>
        </div>
      </SectionCard>

      {/* Point Thresholds */}
      <SectionCard title="Pontuação Mínima" icon="trophy">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Field label="Faixa de alerta (amarelo)">
            <input
              type="number"
              value={current.min_points_warning ?? 1600}
              onChange={(e) => setForm({ ...form, min_points_warning: Number(e.target.value) })}
              className={INPUT_CLASS}
            />
          </Field>
          <Field label="Faixa crítica (vermelho)" hint="0 = desativado">
            <input
              type="number"
              value={current.min_points_critical ?? 0}
              onChange={(e) => setForm({ ...form, min_points_critical: Number(e.target.value) })}
              className={INPUT_CLASS}
            />
          </Field>
        </div>
      </SectionCard>

      {/* Relaxation */}
      <SectionCard title="Relaxamento" icon="flag">
        <div className="flex items-center gap-3">
          <ToggleSwitch
            checked={current.relax_on_first_place ?? true}
            onChange={(checked) => setForm({ ...form, relax_on_first_place: checked })}
            label="Relaxar regras quando o clã garantir 1º lugar"
          />
          <span className="text-sm text-[var(--color-text-secondary)]">
            Relaxar regras quando o clã garantir 1º lugar (vitória antecipada)
          </span>
        </div>
      </SectionCard>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <Button
          variant="primary"
          onClick={handleSave}
          loading={updateMutation.isPending}
          disabled={!hasChanges}
          iconLeft="check"
        >
          Salvar
        </Button>
        <Button
          variant="danger"
          onClick={() => setShowConfirm(true)}
          loading={defaultsMutation.isPending}
          iconLeft="x"
        >
          Restaurar Defaults
        </Button>
      </div>

      <Modal
        open={showConfirm}
        title="Restaurar Defaults"
        destructive
        confirmLabel="Restaurar"
        onConfirm={() => defaultsMutation.mutate()}
        onCancel={() => setShowConfirm(false)}
      >
        Isso irá resetar todas as regras de avaliação para os valores padrão. As alterações não
        salvas serão perdidas. Deseja continuar?
      </Modal>
    </div>
  );
}
