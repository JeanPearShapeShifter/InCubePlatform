export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-md px-4">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight">InCube</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            AI-powered business transformation
          </p>
        </div>
        {children}
      </div>
    </div>
  );
}
