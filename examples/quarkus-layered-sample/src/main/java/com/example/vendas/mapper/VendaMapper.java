package com.example.vendas.mapper;

import com.example.vendas.dto.VendaResponse;
import com.example.vendas.entity.Venda;

import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "jakarta-cdi")
public interface VendaMapper {

    // Problema intencional (BCK-MAP-003): acessa associações por item da lista (cliente e itens).
    @Mapping(target = "cliente", source = "cliente.nome")
    @Mapping(target = "quantidadeItens", expression = "java(venda.itens.size())")
    VendaResponse toResponse(Venda venda);
}
