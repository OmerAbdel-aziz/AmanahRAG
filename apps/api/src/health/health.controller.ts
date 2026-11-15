import { Controller, Get } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";

@Controller("health")
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get()
  async check() {
    const database = await this.prisma.isHealthy();
    return {
      status: database ? "ok" : "degraded",
      service: "api",
      version: process.env.npm_package_version ?? "0.1.0",
      uptimeSeconds: Math.round(process.uptime()),
      checks: { database },
      timestamp: new Date().toISOString(),
    };
  }
}
