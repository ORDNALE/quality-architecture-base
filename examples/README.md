# Exemplos

Projetos **pequenos e fictícios** para exercitar INIT, AUDIT, FIX e REVIEW sem tocar em sistemas
reais. Eles contêm problemas **intencionais**, marcados com comentários no código, e servem de
oráculo para os testes automatizados (`tests/`) e para avaliações manuais da skill.

> Não use estes exemplos como modelo de código. Eles não foram compilados nesta base (não há Maven
> nem dependências npm instaladas); servem à detecção de stack e à análise estática.

## `quarkus-layered-sample/`

Quarkus 3 + Hibernate ORM com Panache + MapStruct + PostgreSQL, perfil arquitetural **layered**
(`.quality/PROJECT_PROFILE.md` já preenchido).

| Problema intencional | Local | Regra | Sinal de `arch_signals.py` |
|---|---|---|---|
| Resource injeta Repository | `resource/ClienteResource.java:18` | ARC-LAY-001 | S-ARC-001 |
| Resource retorna Entity | `resource/ClienteResource.java:23` | BCK-DTO-001 | S-DTO-001 |
| `listAll()` + filtro em memória, sem paginação | `resource/ClienteResource.java:24` | PER-QRY-001, PER-PAG-001 | S-PER-004 |
| `@ManyToOne` sem LAZY (EAGER implícito) | `entity/Venda.java:25` | PER-LOAD-001 | S-PER-002 |
| Repository chamado dentro de laço (N+1) | `service/VendaService.java:39` | PER-N1-001 | S-PER-005 |
| `JOIN FETCH` de coleção + paginação | `repository/VendaRepository.java:24` | PER-PAG-007 (CF-01) | S-PER-006 |
| Mapper navega associações por item (N+1 provável) | `mapper/VendaMapper.java:13-14` | BCK-MAP-003 | S-MAP-001 (parcial) |
| Geração de esquema destrutiva para todos os perfis | `application.properties:5` | BCK-QRK-005 | (via `detect_stack.py`) |
| FK sem índice | `db/migration/V1__init.sql:10` | PER-IDX-001 | — |
| Tamanho de página sem máximo | `resource/VendaResource.java:22` | PER-PAG-004 | — |

Também contém `.quality/plans/PLAN-2026-10-08-cliente-resource-dto.md`, um plano de FIX com
`Status: PENDING`. `fix_gate.py check` deve **recusá-lo** (exit 2), demonstrando que FIX exige
autorização.

## `react-sample/`

React 18 + Vite + TypeScript (o `package-lock.json` é reduzido, apenas para testar a detecção).

| Problema intencional | Local | Regra |
|---|---|---|
| Rota pouco usada importada estaticamente | `src/App.tsx:5-6` | FE-RX-001, FE-COM-001 |
| Busca sem debounce/cancelamento | `src/pages/ClientesPage.tsx:12-18` | FE-COM-004, FE-RX-002 |
| Lista completa filtrada no cliente | `src/pages/ClientesPage.tsx:16` | FE-COM-005 |
| Índice como chave em lista filtrada | `src/pages/ClientesPage.tsx:27` | FE-RX-006 |

## Como exercitar com segurança

Sempre trabalhe numa **cópia** fora deste repositório, para que FIX nunca altere os exemplos
versionados:

```bash
cp -r examples/quarkus-layered-sample /tmp/qab-sample
cd /tmp/qab-sample && git init -q && git add -A && git -c user.name=qab -c user.email=qab@example.invalid commit -qm baseline
```

Depois instale a skill nessa cópia (ver `docs/INSTALLATION.md`) e execute os modos (ver
`docs/USAGE.md`).
