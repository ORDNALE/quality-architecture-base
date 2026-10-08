package com.example.vendas.resource;

import java.util.List;

import com.example.vendas.entity.Cliente;
import com.example.vendas.repository.ClienteRepository;

import jakarta.inject.Inject;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.QueryParam;

@Path("/clientes")
public class ClienteResource {

    // Problema intencional (ARC-LAY-001): Resource acessa Repository diretamente.
    @Inject
    ClienteRepository clienteRepository;

    // Problemas intencionais: BCK-DTO-001 (retorna Entity) e PER-QRY-001 (filtro em memória
    // sobre a tabela inteira, sem paginação — PER-PAG-001).
    @GET
    public List<Cliente> listar(@QueryParam("cidade") String cidade) {
        return clienteRepository.listAll().stream()
                .filter(c -> cidade == null || cidade.equalsIgnoreCase(c.cidade))
                .toList();
    }
}
