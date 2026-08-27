interface Props {
  params: Promise<{ token: string }>;
}

export default async function SharedProfilePage({ params }: Props) {
  const { token } = await params;
  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold">
        Shared Profile ({token}) — stub page
      </h1>
    </div>
  );
}
