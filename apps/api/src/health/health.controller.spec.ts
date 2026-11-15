import { Test } from "@nestjs/testing";
import { HealthController } from "./health.controller";
import { PrismaService } from "../prisma/prisma.service";

describe("HealthController", () => {
  it("reports ok when the database answers", async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [{ provide: PrismaService, useValue: { isHealthy: async () => true } }],
    }).compile();

    const result = await moduleRef.get(HealthController).check();

    expect(result.status).toBe("ok");
    expect(result.checks.database).toBe(true);
  });

  it("reports degraded when the database is unreachable", async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [{ provide: PrismaService, useValue: { isHealthy: async () => false } }],
    }).compile();

    const result = await moduleRef.get(HealthController).check();

    expect(result.status).toBe("degraded");
  });
});
