import { Injectable } from "@nestjs/common";
import type { Prisma } from "@prisma/client";
import { PrismaService } from "../prisma/prisma.service";
import { CreateDocumentDto } from "./dto/create-document.dto";

@Injectable()
export class DocumentsService {
  constructor(private readonly prisma: PrismaService) {}

  list() {
    return this.prisma.document.findMany({
      orderBy: { createdAt: "desc" },
      take: 100,
      select: {
        id: true,
        title: true,
        language: true,
        status: true,
        createdAt: true,
        _count: { select: { chunks: true } },
      },
    });
  }

  findOne(id: string) {
    return this.prisma.document.findUnique({
      where: { id },
      include: {
        jobs: { orderBy: { queuedAt: "desc" }, take: 10 },
        _count: { select: { chunks: true } },
      },
    });
  }

  /**
   * Registers document metadata. The actual file goes to object storage; this row is the
   * control-plane record. Publishing `document.uploaded.v1` to RabbitMQ belongs here and is
   * deliberately not wired until storage is chosen (see docs/adr/0002).
   */
  create(dto: CreateDocumentDto) {
    return this.prisma.document.create({
      data: {
        title: dto.title,
        filename: dto.filename,
        mimeType: dto.mimeType,
        language: dto.language,
        sizeBytes: dto.sizeBytes,
        checksum: dto.checksum,
        metadata: (dto.metadata ?? {}) as Prisma.InputJsonValue,
      },
    });
  }
}
