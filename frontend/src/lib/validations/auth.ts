import * as z from "zod"

export const signInSchema = z.object({
  email: z.string().email({
    message: "Email inválido.",
  }),
  password: z.string().min(1, {
    message: "A senha é obrigatória.",
  }),
  remember: z.boolean().default(false).optional(),
})

export const signUpSchema = z.object({
  full_name: z.string().min(2, {
    message: "Nome deve ter pelo menos 2 caracteres.",
  }).optional().or(z.literal("")),
  email: z.string().email({
    message: "Email inválido.",
  }),
  password: z.string().min(8, {
    message: "A senha deve ter pelo menos 8 caracteres.",
  }),
})

export type SignInValues = z.infer<typeof signInSchema>
export type SignUpValues = z.infer<typeof signUpSchema>
