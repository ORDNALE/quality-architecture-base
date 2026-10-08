package com.example.vendas.repository;

import java.util.List;

import com.example.vendas.entity.Venda;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import io.quarkus.panache.common.Page;
import io.quarkus.panache.common.Sort;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class VendaRepository implements PanacheRepository<Venda> {

    public List<Venda> listarPagina(int pagina, int tamanho) {
        return findAll(Sort.by("dataVenda").descending().and("id"))
                .page(Page.of(pagina, tamanho))
                .list();
    }

    // Problema intencional (PER-PAG-007 / CF-01): JOIN FETCH de coleção com paginação
    // faz o Hibernate paginar em memória.
    public List<Venda> listarPaginaComItens(int pagina, int tamanho) {
        return find("select distinct v from Venda v left join fetch v.itens order by v.id")
                .page(Page.of(pagina, tamanho))
                .list();
    }
}
