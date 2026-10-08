package com.example.vendas.resource;

import java.util.List;

import com.example.vendas.dto.VendaResponse;
import com.example.vendas.service.VendaService;

import jakarta.inject.Inject;
import jakarta.ws.rs.DefaultValue;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.QueryParam;

@Path("/vendas")
public class VendaResource {

    @Inject
    VendaService vendaService;

    @GET
    public List<VendaResponse> listar(@QueryParam("pagina") @DefaultValue("0") int pagina,
                                      @QueryParam("tamanho") @DefaultValue("20") int tamanho) {
        // Observação (PER-PAG-004): sem tamanho máximo de página.
        return vendaService.listar(pagina, tamanho);
    }
}
