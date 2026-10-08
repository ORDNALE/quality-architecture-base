// Exemplo didático para regras de frontend (não é um app completo).
import { BrowserRouter, Route, Routes } from "react-router-dom";
// Problema intencional (FE-RX-001 / FE-COM-001): relatórios pesados e pouco usados entram no
// bundle inicial por importação estática.
import ClientesPage from "./pages/ClientesPage";
import RelatoriosPage from "./pages/RelatoriosPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ClientesPage />} />
        <Route path="/relatorios" element={<RelatoriosPage />} />
      </Routes>
    </BrowserRouter>
  );
}
