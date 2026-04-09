# frontend/ — Aplicación Web AgriScore

Dashboard para agricultores e instituciones financieras. Construido con Next.js 16 (App Router), React 19 y Tailwind CSS 4.

## Por qué Next.js + Tailwind

- **App Router** — Componentes de servidor por defecto, layouts anidados, y routing basado en archivos. Reduce JS enviado al cliente.
- **React 19** — Hooks optimizados y mejor manejo de estado asíncrono.
- **Tailwind CSS 4** — Utilidad-first sin archivos CSS custom. Consistencia visual rápida para hackathon sin sacrificar calidad de UI.
- **TypeScript** — Tipado estricto para interfaces de datos del backend (scores, perfiles, retos).

## Estructura de Páginas

```
src/app/
├── page.tsx          # Splash / landing
├── layout.tsx        # Layout raíz (fuentes, metadata, providers)
├── inicio/           # Dashboard principal — score actual, resumen diario
├── cultivo/          # Mapa satelital de parcela, tarjetas de parcelas
├── reporte/          # Reporte crediticio — gauge de score, historial, créditos
├── retos/            # Gamificación — retos mensuales para mejorar score
└── perfil/           # Perfil del agricultor — datos personales, parcelas
```

## Componentes

```
src/components/
├── layout/           # Estructura de la app
│   ├── AppShell      #   Shell desktop con sidebar
│   ├── MobileShell   #   Shell movil con bottom nav
│   ├── SideNav       #   Navegación lateral
│   └── BottomNav     #   Navegación inferior móvil
│
├── dashboard/        # Widgets del dashboard
│   ├── ScoreView     #   Gauge circular del AgriScore (300-850)
│   └── DailySummary  #   Resumen de actividad diaria
│
├── cultivo/          # Modulo de cultivo
│   ├── SatelliteMap  #   Mapa satelital interactivo (NDVI/RGB)
│   └── ParcelCard    #   Tarjeta de información de parcela
│
├── reporte/          # Módulo de reporte crediticio
│   ├── ScoreOverview #   Gauge lineal + grafica de historial
│   └── LinkedCredits #   Creditos vinculados al perfil
│
├── retos/
│   └── ChallengeCard #   Tarjeta de reto con progreso
│
└── ui/               # Componentes base reutilizables
    ├── ScoreGauge    #   Gauge radial (arco 270°, escala 300-850)
    ├── LinearGauge   #   Barra horizontal con segmentos de riesgo
    ├── LineChart     #   Gráfica de línea para historial de score
    ├── Card          #   Contenedor base con sombra
    ├── ProgressBar   #   Barra de progreso
    ├── TrafficLight  #   Indicador semáforo (bajo/moderado/alto)
    ├── InfoPill      #   Etiqueta informativa
    ├── TogglePill    #   Tab toggle (2 opciones)
    └── WhatsAppFAB   #   Botón flotante para abrir WhatsApp
```

## Datos

El frontend opera en dos modos:

| Modo | Fuente | Cuándo |
|------|--------|--------|
| **Mock** | `src/lib/mock-data.ts` | Sin backend conectado (demo, desarrollo UI) |
| **API** | `src/lib/api.ts` → backend | Backend corriendo en `localhost:8001` o produccion |

El hook `use-farmer-data.ts` abstrae la fuente — los componentes no saben si los datos son mock o reales.

**Escala de scores:** El backend envia scores directamente en escala 300-850. No hay conversión en el frontend.

## Desarrollo Local

```bash
cd frontend
npm install
npm run dev       # http://localhost:3000
npm run build     # Build de produccion
npm run lint      # ESLint
```

Para conectar con el backend local, configurar la URL base en `src/lib/api.ts`.
