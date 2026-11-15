import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { DocumentsModule } from "./documents/documents.module";
import { HealthModule } from "./health/health.module";
import { PrismaModule } from "./prisma/prisma.module";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: [".env", "../../.env"],
    }),
    PrismaModule,
    HealthModule,
    DocumentsModule,
  ],
})
export class AppModule {}
