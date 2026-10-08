import { useEffect, useState } from "react";

type Cliente = { id: number; nome: string; cidade: string };

export default function ClientesPage() {
  const [termo, setTermo] = useState("");
  const [clientes, setClientes] = useState<Cliente[]>([]);

  // Problemas intencionais: FE-COM-004 / FE-RX-002 (requisição a cada tecla, sem debounce e sem
  // cancelamento — respostas antigas podem sobrescrever novas) e FE-COM-005 (lista completa
  // filtrada no cliente).
  useEffect(() => {
    fetch("/api/clientes")
      .then((r) => r.json())
      .then((todos: Cliente[]) =>
        setClientes(todos.filter((c) => c.nome.toLowerCase().includes(termo.toLowerCase()))),
      );
  }, [termo]);

  return (
    <main>
      <label htmlFor="busca">Buscar cliente</label>
      <input id="busca" value={termo} onChange={(e) => setTermo(e.target.value)} />
      <ul>
        {clientes.map((c, index) => (
          // FE-RX-006: índice como chave em lista filtrada.
          <li key={index}>
            {c.nome} — {c.cidade}
          </li>
        ))}
      </ul>
    </main>
  );
}
