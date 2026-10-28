import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-semibold cursor-pointer transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-r from-emerald-600 to-teal-600 text-white border border-emerald-400/30 shadow-[0_4px_16px_rgba(16,185,129,0.28)] hover:from-emerald-500 hover:to-cyan-600 hover:shadow-[0_6px_22px_rgba(16,185,129,0.42)] hover:-translate-y-0.5 active:translate-y-0",
        destructive:
          "bg-destructive text-destructive-foreground border border-red-400/30 shadow-[0_4px_14px_rgba(239,68,68,0.25)] hover:bg-destructive/90",
        outline:
          "border border-border bg-card/70 backdrop-blur-md text-foreground shadow-sm hover:border-primary/60 hover:bg-accent hover:text-accent-foreground hover:shadow-[0_0_16px_rgba(16,185,129,0.16)]",
        secondary:
          "bg-secondary text-secondary-foreground border border-border/70 shadow-sm hover:bg-secondary/80 hover:border-primary/40",
        ghost:
          "text-foreground/85 hover:bg-accent/80 hover:text-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-11 rounded-lg px-7 text-sm",
        icon: "h-9 w-9 rounded-lg",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
