"use client";

import { useAuthStore } from "@/stores/auth-store";
import { useThemeStore, type Theme } from "@/stores/theme-store";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu";
import { Menu, LogOut, Settings, User, Sun } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface HeaderProps {
  onMenuToggle: () => void;
}

const themes: { value: Theme; label: string }[] = [
  { value: "space", label: "Space" },
  { value: "forest", label: "Forest" },
  { value: "blackhole", label: "Black Hole" },
];

export function Header({ onMenuToggle }: HeaderProps) {
  const { user, logout } = useAuthStore();
  const { theme, setTheme } = useThemeStore();
  const router = useRouter();

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "?";

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <header className="flex h-14 items-center justify-between border-b border-border bg-card px-4">
      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuToggle}
        >
          <Menu className="h-5 w-5" />
        </Button>
        <Link href="/dashboard" className="text-lg font-bold tracking-tight">
          InCube
        </Link>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary text-primary-foreground text-xs">
                {initials}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <div className="flex flex-col space-y-1">
              <p className="text-sm font-medium">{user?.full_name ?? "User"}</p>
              <p className="text-xs text-muted-foreground">
                {user?.email ?? ""}
              </p>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem asChild>
            <Link href="/settings">
              <User className="mr-2 h-4 w-4" />
              Profile
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link href="/settings">
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </Link>
          </DropdownMenuItem>
          <DropdownMenuSub>
            <DropdownMenuSubTrigger>
              <Sun className="mr-2 h-4 w-4" />
              Theme: {themes.find((t) => t.value === theme)?.label}
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent>
              {themes.map((t) => (
                <DropdownMenuItem key={t.value} onClick={() => setTheme(t.value)}>
                  {t.label}
                  {theme === t.value && " (active)"}
                </DropdownMenuItem>
              ))}
            </DropdownMenuSubContent>
          </DropdownMenuSub>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" />
            Logout
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
