package com.example.vendas.service;

import java.math.BigDecimal;
import java.util.List;

import com.example.vendas.dto.VendaResponse;
import com.example.vendas.entity.ItemVenda;
import com.example.vendas.entity.Venda;
import com.example.vendas.mapper.VendaMapper;
import com.example.vendas.repository.ItemVendaRepository;
import com.example.vendas.repository.VendaRepository;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class VendaService {

    @Inject
    VendaRepository vendaRepository;

    @Inject
    ItemVendaRepository itemVendaRepository;

    @Inject
    VendaMapper vendaMapper;

    public List<VendaResponse> listar(int pagina, int tamanho) {
        return vendaRepository.listarPagina(pagina, tamanho).stream()
                .map(vendaMapper::toResponse)
                .toList();
    }

    /** Regra de negócio: soma de quantidade × preço unitário, preservando escala do banco. */
    public BigDecimal totalItens(List<Venda> vendas) {
        BigDecimal total = BigDecimal.ZERO;
        for (Venda venda : vendas) {
            // Problema intencional (PER-N1-001): consulta ao repositório por venda.
            List<ItemVenda> itens = itemVendaRepository.doVenda(venda.id);
            for (ItemVenda item : itens) {
                total = total.add(item.precoUnitario.multiply(BigDecimal.valueOf(item.quantidade)));
            }
        }
        return total;
    }
}
