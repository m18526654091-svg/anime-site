// AnimeHub 前端版本标识
// 构建时通过 NEXT_PUBLIC_APP_VERSION / NEXT_PUBLIC_APP_BUILD_TIME 注入，
// 便于线上快速确认前端运行版本；未注入时回退默认值。
export const VERSION: string =
  process.env.NEXT_PUBLIC_APP_VERSION || "1.7.0";
export const BUILD_TIME: string =
  process.env.NEXT_PUBLIC_APP_BUILD_TIME || "development";
export const ENVIRONMENT: string =
  process.env.NEXT_PUBLIC_ENV || "development";
