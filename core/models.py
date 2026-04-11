from django.db import models

class CategoriaTabela(models.Model):
    id_legado = models.IntegerField(unique=True, null=True, blank=True)
    tipo = models.CharField(max_length=50) 
    codigo = models.CharField(max_length=20, null=True, blank=True)
    descricao = models.CharField(max_length=255)

    def __str__(self):
        if self.tipo == 'CNAE' and self.codigo:
            return f"{self.codigo} - {self.descricao}"
        return self.descricao
    
class Empresa(models.Model):
    razao_social = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    # Novo campo NIRE
    nire = models.CharField(max_length=50, blank=True, null=True, verbose_name="NIRE")
    
    endereco = models.CharField(max_length=255, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    capital_social = models.DecimalField(max_digits=15, decimal_places=2, default=0.0, null=True, blank=True)
    inicio_atividade = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    cnae_principal = models.ForeignKey(CategoriaTabela, on_delete=models.SET_NULL, null=True, blank=True, related_name='empresas_cnae')
    # Removido situacao_empresa e mantidos os outros
    tipo_empresa = models.ForeignKey(CategoriaTabela, on_delete=models.SET_NULL, null=True, blank=True, related_name='empresas_tipo')
    regime_tributacao = models.ForeignKey(CategoriaTabela, on_delete=models.SET_NULL, null=True, blank=True, related_name='empresas_regime')
    situacao_cadastro = models.ForeignKey(CategoriaTabela, on_delete=models.SET_NULL, null=True, blank=True, related_name='empresas_sit_cad')

    def __str__(self):
        return self.razao_social

# O modelo Socio permanece igual...

class Socio(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="socios")
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=20, blank=True, null=True)
    valor_participacao = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    def __str__(self):
        return self.nome