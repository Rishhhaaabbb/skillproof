interface Props {
  params: Promise<{ id: string }>;
}

export default async function ComparisonPage({ params }: Props) {
  const { id } = await params;
  return (
    <div className="p-8">
      <h1 className="text-2xl font-semibold">
        Comparison for Role {id} — stub page
      </h1>
    </div>
  );
}
