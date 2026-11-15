import { Body, Controller, Get, NotFoundException, Param, Post } from "@nestjs/common";
import { DocumentsService } from "./documents.service";
import { CreateDocumentDto } from "./dto/create-document.dto";

@Controller("documents")
export class DocumentsController {
  constructor(private readonly documents: DocumentsService) {}

  @Get()
  list() {
    return this.documents.list();
  }

  @Get(":id")
  async findOne(@Param("id") id: string) {
    const document = await this.documents.findOne(id);
    if (!document) {
      throw new NotFoundException("document not found");
    }
    return document;
  }

  @Post()
  create(@Body() dto: CreateDocumentDto) {
    return this.documents.create(dto);
  }
}
