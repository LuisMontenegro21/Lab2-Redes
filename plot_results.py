# plot_results.py
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "results.csv"

def abort(msg):
    print(f"[!] {msg}")
    sys.exit(1)

def safe_save(fig_name):
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.clf()
    print(f"[ok] Guardado: {fig_name}")

def to_float_safe(x):
    try:
        return float(str(x).strip())
    except Exception:
        return None

def main():
    if not os.path.exists(CSV_PATH):
        abort(f"No se encontró {CSV_PATH}. ¿Ya corriste el server y enviaste mensajes?")

    df = pd.read_csv(CSV_PATH)

    if df.empty:
        abort("results.csv existe pero no tiene filas. Corre el server y envía mensajes desde los clientes.")

    # Normalizar columnas esperadas
    if "alg" not in df.columns:
        abort("results.csv no tiene columna 'alg'. Revisa que el server esté registrando 'alg' correctamente.")

    if "outcome" not in df.columns:
        abort("results.csv no tiene columna 'outcome'. Revisa el logger del server.")

    # Normaliza texto
    df["alg"] = df["alg"].astype(str).str.upper().str.strip()
    df["outcome"] = df["outcome"].astype(str).str.strip()

    # Filtra filas útiles
    useful = df[ df["alg"].isin(["CRC","HAM"]) ]
    if useful.empty:
        abort("No hay filas con alg=CRC o HAM. ¿El cliente está mandando 'CRC:' o 'HAM:'?")

    # Éxito por algoritmo: CRC -> ok; HAM -> ok o corrected
    useful = useful.copy()
    useful["success"] = False
    useful.loc[(useful["alg"]=="CRC") & (useful["outcome"]=="ok"), "success"] = True
    useful.loc[(useful["alg"]=="HAM") & (useful["outcome"].isin(["ok","corrected"])), "success"] = True

    # 1) tasa de éxito por algoritmo
    rate_by_alg = useful.groupby("alg")["success"].mean()
    if rate_by_alg.empty:
        print("[i] No hay datos suficientes para 'rate_by_alg'.")
    else:
        ax = rate_by_alg.plot(kind="bar", rot=0)
        ax.set_title("Tasa de éxito por algoritmo")
        ax.set_ylabel("Éxito (0..1)")
        ax.set_xlabel("Algoritmo")
        safe_save("rate_by_alg.png")

    # 2) éxito vs longitud (si existe len_bits)
    if "len_bits" in useful.columns and useful["len_bits"].notna().any():
        gb = useful.dropna(subset=["len_bits"]).copy()
        # Asegura tipo numérico
        gb["len_bits"] = pd.to_numeric(gb["len_bits"], errors="coerce")
        gb = gb.dropna(subset=["len_bits"])
        if not gb.empty:
            lines_plotted = 0
            for alg, sub in gb.groupby("alg"):
                series = sub.groupby("len_bits")["success"].mean().sort_index()
                if not series.empty:
                    plt.plot(series.index, series.values, marker="o", label=alg)
                    lines_plotted += 1
            if lines_plotted > 0:
                plt.title("Éxito vs longitud (bits)")
                plt.xlabel("Longitud (bits)")
                plt.ylabel("Éxito (0..1)")
                plt.legend()
                safe_save("success_vs_length.png")
            else:
                print("[i] No hay datos para graficar éxito vs longitud.")
        else:
            print("[i] 'len_bits' está vacío tras limpieza; se omite gráfica de longitud.")
    else:
        print("[i] No existe columna 'len_bits' o no tiene datos; se omite gráfica de longitud.")

    # 3) éxito vs probabilidad de error p (si existe meta_p)
    if "meta_p" in useful.columns and useful["meta_p"].notna().any():
        gp = useful.copy()
        gp["p"] = gp["meta_p"].map(to_float_safe)
        gp = gp.dropna(subset=["p"])
        if not gp.empty:
            lines_plotted = 0
            for alg, sub in gp.groupby("alg"):
                series = sub.groupby("p")["success"].mean().sort_index()
                if not series.empty:
                    plt.plot(series.index, series.values, marker="o", label=alg)
                    lines_plotted += 1
            if lines_plotted > 0:
                plt.title("Éxito vs prob. de error (p)")
                plt.xlabel("p (probabilidad de flip por bit)")
                plt.ylabel("Éxito (0..1)")
                plt.legend()
                safe_save("success_vs_p.png")
            else:
                print("[i] No hay datos para graficar éxito vs p.")
        else:
            print("[i] meta_p no tiene valores numéricos; se omite gráfica de p.")
    else:
        print("[i] No existe columna 'meta_p' o no tiene datos; se omite gráfica de p.")

    print("[done] Revisa los .png generados (si hubo datos).")

if __name__ == "__main__":
    main()
