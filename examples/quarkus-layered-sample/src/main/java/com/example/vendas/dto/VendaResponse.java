package com.example.vendas.dto;

import java.math.BigDecimal;
import java.time.LocalDate;

public record VendaResponse(Long id, String cliente, LocalDate dataVenda, BigDecimal total, int quantidadeItens) {
}
