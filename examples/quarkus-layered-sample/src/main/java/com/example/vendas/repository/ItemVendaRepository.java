package com.example.vendas.repository;

import java.util.List;

import com.example.vendas.entity.ItemVenda;

import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class ItemVendaRepository implements PanacheRepository<ItemVenda> {

    public List<ItemVenda> doVenda(Long vendaId) {
        return list("venda.id", vendaId);
    }
}
