package com.example.vendas.entity;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;

@Entity
public class Venda {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;

    // Problema intencional (PER-LOAD-001): @ManyToOne sem LAZY é EAGER por padrão no JPA.
    @ManyToOne
    @JoinColumn(name = "cliente_id")
    public Cliente cliente;

    @Column(name = "data_venda")
    public LocalDate dataVenda;

    public BigDecimal total;

    @OneToMany(mappedBy = "venda")
    public List<ItemVenda> itens = new ArrayList<>();
}
