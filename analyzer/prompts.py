import json
from typing import Dict, Any

SYSTEM_INSTRUCTION = """Sen milyonlarca kişiye ulaşan viral psikoloji bültenleri, Instagram Reels senaryoları ve derinlikli sosyal medya içerikleri kurgulayan kıdemli bir içerik mimarısın.

Görevin: Verilen yabancı psikoloji makalesini yüzeyselleştirmeden, kısa kesmeden ve bilimsel derinliğini koruyarak; doğrudan paylaşıma hazır, son derece akıcı, samimi ve kancası içine yedirilmiş tek bir Türkçe içerik metnine dönüştürmektir.

METNİN KURGUSU (Kancalar ayrı bir liste değil, doğrudan metnin içine yedirilmelidir):
1. AÇILIŞ (Kanca / Hook & Çatışma): Metin ilk 1-2 cümlesinde kaydırmayı bıçak gibi durduran ezber bozan bir iddia, yaygın bir yanlışı yıkan tezat veya sarsıcı bir tespitle DOĞRUDAN başlamalıdır.
2. GELİŞME (Ayna Etkisi & Kapsamlı Anlatım): Okuyucuya 'Aynı beni anlatıyor!' dedirten insani tespitler yapılmalı; makaledeki psikolojik mekanizmalar, kavramlar ve vaka örnekleri adam akıllı, doyurucu ve kapsamlı bir şekilde açıklanmalıdır. Asla kısa kesilmemeli, konunun hakkı tam verilmelidir.
3. SONUÇ (Kaydetme Gücü & Çözüm): Okuyucunun 'Bunu mutlaka kaydetmeliyim' diyeceği hap tavsiyeler, adımlar veya pratik yöntemlerle güçlü bir kapanış yapılmalıdır.

DİKKAT EDİLECEK HUSUSLAR:
- 'kancalar' diye ayrı bir alan AÇMA; kanca metnin ilk cümlesi olmalıdır.
- Metni kısa kesme; kapsamlı, doyurucu, akıcı paragraflar ve maddelerle tam bir sosyal medya/blog yazısı olarak hazırla.
- Yanıtını SADECE geçerli bir JSON nesnesi olarak döndür."""

def build_analysis_prompt(article_data: Dict[str, Any]) -> str:
    title = article_data.get("title", "")
    summary = article_data.get("summary", "")
    key_points = article_data.get("key_points", [])
    sections = article_data.get("sections", [])
    
    # Kapsamlı özetleme için makalenin dolu içeriğini derle
    body_snippets = []
    if sections:
        for s in sections[:8]:
            h = s.get("heading", "")
            c = s.get("content", "")
            if c:
                body_snippets.append(f"### {h}\n{c[:500]}")
        body = "\n\n".join(body_snippets)
    else:
        body = article_data.get("raw_markdown", "")[:4000]

    prompt = f"""Aşağıdaki psikoloji konusunu; kancası açılışına yedirilmiş, adam akıllı derinlemesine işlenmiş ve kaydetme dürtüsü uyandıran kapsamlı bir Türkçe sosyal medya içerik metnine dönüştür:

KONU: {title}
ÖZET: {summary}
ANAHTAR NOKTALAR: {json.dumps(key_points[:8], ensure_ascii=False) if key_points else "Yok"}
DETAYLAR:
{body}

BEKLENEN JSON FORMATI:
{{
  "baslik": "Kaydırmayı durduran merak uyandırıcı Türkçe başlık",
  "kategori": "Örn: İlişkiler & Sosyal Psikoloji, Narsisizm, Duygu Yönetimi",
  "metin": "İlk cümlesi doğrudan çarpıcı kancayla başlayan; konuyu yüzeyselleştirmeden, psikolojik mekanizmasını ve insan hayatındaki yansımasını kapsamlıca anlatan; sonunda kaydetmeyi tetikleyen pratik adımlarla biten zengin ve akıcı Türkçe içerik metni.",
  "puan": 92
}}
"""
    return prompt
