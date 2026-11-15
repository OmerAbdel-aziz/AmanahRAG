import { DocumentLanguage } from "@prisma/client";
import { IsEnum, IsInt, IsObject, IsOptional, IsString, MaxLength, Min } from "class-validator";

export class CreateDocumentDto {
  @IsString()
  @MaxLength(200)
  title!: string;

  @IsString()
  @MaxLength(255)
  filename!: string;

  @IsString()
  @MaxLength(120)
  mimeType!: string;

  @IsEnum(DocumentLanguage)
  language!: DocumentLanguage;

  @IsInt()
  @Min(1)
  sizeBytes!: number;

  /** SHA-256 of the original file; used for de-duplication. */
  @IsString()
  @MaxLength(64)
  checksum!: string;

  @IsOptional()
  @IsObject()
  metadata?: Record<string, unknown>;
}
